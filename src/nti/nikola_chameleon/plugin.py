# -*- coding: utf-8 -*-
"""
The Chameleon ZPT plugin for nikola.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports
from collections import defaultdict
import glob
import os
import os.path


from nikola.plugin_categories import TemplateSystem
from nikola.utils import makedirs
from z3c.macro.interfaces import IMacroTemplate

from z3c.macro.zcml import MacroFactory


from zope import component
from zope import interface

from zope.browserpage.simpleviewclass import SimpleViewClass

from zope.configuration import xmlconfig
from zope.dottedname import resolve as dottedname

import nti.nikola_chameleon
from nti.nikola_chameleon import interfaces
from .request import Request
from .interfaces import ITemplate
from .template import ViewPageTemplateFileWithLoad
from .template import TemplateFactory

logger = __import__('logging').getLogger(__name__)

class Context(object):
    """
    Instances of this object will be the context
    of a template when no post is available.
    """

class ChameleonTemplates(TemplateSystem):

    name = 'nti.nikola_chameleon'

    def __init__(self):
        super(ChameleonTemplates, self).__init__()
        self._conf_context = xmlconfig.file('configure.zcml', nti.nikola_chameleon)
        self._template_paths = []
        self._injected_template_paths = []

    def set_directories(self, directories, cache_folder):
        """Sets the list of folders where templates are located and cache."""
        # A list of directories where the templates will be
        # located. Most template systems have some sort of
        # template loading tool that can use this.

        # They are passed from most specific (project templates)
        # to least specific (parent themes), so we need to reverse the order
        # so that more specific templates are registered last and thus
        # override.
        self._template_paths.extend(reversed(directories))

        # We do set up the cache, though.

        cache_dir = None
        if  not 'CHAMELEON_CACHE' in os.environ or \
            not os.path.isdir(os.path.expanduser(os.environ['CHAMELEON_CACHE'])):
            cache_dir = os.path.abspath(os.path.join(cache_folder, 'chameleon_cache'))
            makedirs(cache_dir)
            os.environ['CHAMELEON_CACHE'] = cache_dir
        else:
            cache_dir = os.environ['CHAMELEON_CACHE']

        conf_mod = dottedname.resolve('chameleon.config')
        if conf_mod.CACHE_DIRECTORY != cache_dir:
            # previously imported before we set the environment
            conf_mod.CACHE_DIRECTORY = cache_dir
            # Which, snarf, means the template is probably also screwed up.
            # It imports all of this stuff statically, and BaseTemplate
            # statically creates a default loader at import time
            template_mod = dottedname.resolve('chameleon.template')
            if template_mod.CACHE_DIRECTORY != conf_mod.CACHE_DIRECTORY:
                template_mod.CACHE_DIRECTORY = conf_mod.CACHE_DIRECTORY
                template_mod.BaseTemplate.loader = template_mod._make_module_loader()

            # Creating these guys with debug or autoreload, as Pyramid does when its
            # debug flags are set, will override this setting
        return

    def template_deps(self, template_name):
        """Returns filenames which are dependencies for a template."""
        # You *must* implement this, even if to return []
        # It should return a list of all the files that,
        # when changed, may affect the template's output.
        # usually this involves template inheritance and
        # inclusion.
        #
        # XXX: I don't know how to implement this for Chameleon,
        # especially not if we enable macros.
        return []

    get_deps = template_deps
    get_string_deps = template_deps

    def render_template(self, template_name, output_name, context):
        """Renders template to a file using context.

        This must save the data to output_name *and* return it
        so that the caller may do additional processing.
        """
        result = self.render_template_to_string(template_name, context)
        if output_name is not None:
            makedirs(os.path.dirname(output_name))
            with open(output_name, 'wb') as f:
                f.write(result.encode('utf-8'))
        return result

    def render_template_to_string(self, template, context):
        """Renders template to a string using context. """
        # The method that does the actual rendering.
        # template_name is the name of the template file,
        # context is a dictionary containing the data the template
        # uses for rendering.
        self._provide_templates()

        # context becomes the options dict.
        options = context
        # self becomes view.
        view = self
        # The post, if given, becomes the context.
        # Otherwise, it's a dummy object.
        context = options.get('post')

        if context is not None:
            # We only render these things once in a given run,
            # so we don't bother stripping the interfaces off of it
            # or using a proxy.
            assert not interfaces.IPageKind.providedBy(context)
            interface.alsoProvides(context, interfaces.IPostPage)
        else:
            context = Context()

        request = Request(context, options)
        # apply the "layer" to the request
        pagekind = frozenset(options.get('pagekind', ()))
        interface.alsoProvides(request, interfaces.PAGEKINDS[pagekind])

        template = component.getMultiAdapter((context, request),
                                             ITemplate,
                                             name=template)


        # Make the context available.
        # zope.browserpage, assumes it's on the view object.
        # chameleon/z3c.pt will use the kwargs

        options['context'] = context
        # The ViewPageTemplate likes to have a request. We provide
        # a new object so that it can have access to the context variables.
        return template(view, request=request, **options)

    def inject_directory(self, directory):
        """Injects the directory with the lowest priority in the
        template search mechanism."""

        # This is called very early, that's the only reason that it gets
        # set low in the chains. It's called for each template plugin?
        self._injected_template_paths.append(directory)

    def _provide_templates(self):
        for d in self._injected_template_paths:
            self._provide_templates_from_directory(d)
        self._injected_template_paths = []

        for d in self._template_paths:
            self._provide_templates_from_directory(d)
        self._template_paths = []

    def _provide_templates_from_directory(self, directory):
        if not isinstance(directory, str) and str is bytes:
            # nikola likes to provide these as unicode on Python 2,
            # which is incorrect (unless maybe on windows?)
            # Ideally we'd decode using the filesystem decoding or something,
            # right now we just assume the locale decodes right.
            directory = directory.encode("utf-8")

        directory = os.path.abspath(directory)

        seen_macros = defaultdict(set)
        # Register macros for each macro found in each .macro.pt
        # file. This doesn't deal with naming conflicts.
        gsm = component.getGlobalSiteManager()
        for macro_file in sorted(glob.glob(os.path.join(directory, "*.macro.pt"))):
            template = ViewPageTemplateFileWithLoad(macro_file)
            for name in template.macros.names:
                factory = MacroFactory(macro_file, name, 'text/html')
                if name in seen_macros:
                    logger.warning("Duplicate macro '%s' in %s and %s",
                                   name, seen_macros[name], macro_file)
                seen_macros[name].add(macro_file)
                gsm.registerAdapter(factory,
                                    provided=(IMacroTemplate),
                                    required=(interface.Interface, interface.Interface,
                                              interface.Interface),
                                    name=name)


        for template_file in sorted(glob.glob(os.path.join(directory, "*.tmpl.pt"))):

            name = os.path.basename(template_file)
            name = name[:-len(".pt")]
            factory = TemplateFactory(template_file)
            # Register them as template adapters for us.
            gsm.registerAdapter(factory,
                                provided=(ITemplate),
                                required=(interface.Interface, interface.Interface),
                                name=name)

            # Register them as views for traversing
            gsm.registerAdapter(SimpleViewClass(template_file, offering='', name=name),
                                provided=interface.Interface,
                                required=(interface.Interface, interface.Interface),
                                name=name)

        theme_zcml = os.path.join(directory, 'theme.zcml')
        if os.path.exists(theme_zcml):
            # Let any explicit directions take precedence.
            xmlconfig.file(theme_zcml, context=self._conf_context)
