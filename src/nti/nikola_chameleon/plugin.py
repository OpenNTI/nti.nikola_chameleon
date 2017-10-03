# -*- coding: utf-8 -*-
"""
The Chameleon ZPT plugin for nikola.

"""
from __future__ import absolute_import, division, print_function

import glob
import os
import os.path

from chameleon.zpt.template import PageTemplateFile
from nikola.plugin_categories import TemplateSystem
from nikola.utils import makedirs

import nti.nikola_chameleon
import z3c.pt.pagetemplate
from z3c.macro.interfaces import IMacroTemplate
from z3c.macro.zcml import MacroFactory
import z3c.macro.zcml
from zope import component
from zope import interface
from zope.configuration import xmlconfig
from zope.dottedname import resolve as dottedname
from zope.publisher.interfaces import IRequest
from zope.browserpage.simpleviewclass import SimpleViewClass
import zope.browserpage.simpleviewclass


logger = __import__('logging').getLogger(__name__)

class _ViewPageTemplateFileWithLoad(z3c.pt.pagetemplate.ViewPageTemplateFile):
    """
    Enables the load: expression type for convenience.
    """
    # NOTE: We cannot do the rational thing and copy this
    # and modify our local value. This is because
    # certain packages, notably z3c.macro,
    # modify the superclass's value; depending on the order
    # of import, we may or may not get that change.
    # So we do the bad thing too and modify the superclass also

    @property
    def builtins(self):
        d = super(_ViewPageTemplateFileWithLoad, self).builtins
        d['__loader'] = self._loader
        return d

z3c.pt.pagetemplate.BaseTemplate.expression_types['structure'] =  PageTemplateFile.expression_types['structure']
z3c.pt.pagetemplate.BaseTemplate.expression_types['load'] = PageTemplateFile.expression_types['load']
z3c.macro.zcml.ViewPageTemplateFile = _ViewPageTemplateFileWithLoad
zope.browserpage.simpleviewclass.ViewPageTemplateFile = _ViewPageTemplateFileWithLoad

class ITemplate(interface.Interface):
    """
    A template.
    """

class TemplateFactory(object):

    def __init__(self, path):
        self.path = path

    def __call__(self, *_ignored):
        return _ViewPageTemplateFileWithLoad(self.path)

@interface.implementer(IRequest)
class Request(object):
    # Minimum request-like object to use when rendering
    # We claim to implement zope.publisher's IRequest in order to
    # be able to use all the pre-registered adapters.
    response = None

class ChameleonTemplates(TemplateSystem):

    name = 'nti.nikola_chameleon'

    def __init__(self):
        super(ChameleonTemplates, self).__init__()
        xmlconfig.file('configure.zcml', nti.nikola_chameleon)

    def set_directories(self, directories, cache_folder):
        """Sets the list of folders where templates are located and cache."""
        # A list of directories where the templates will be
        # located. Most template systems have some sort of
        # template loading tool that can use this.

        # But we can get macros and etc from the directory.
        # XXX What about entire templates? We need a way to deal
        # with those. Zope would use a <page> or <view> directive.
        # The Chamelean PageTemplateFile supports a 'search_path' argument,
        # and theoretically that could be passed through all the layers.

        # They are passed from most specific (project templates)
        # to least specific (parent themes), so we need to reverse the order
        # so that more specific templates are registered last and thus
        # override.
        for d in reversed(directories):
            self._provide_templates_from_directory(d)

        # We do set up the cache, though.

        cache_dir = None
        if  not 'CHAMELEON_CACHE' in os.environ or \
            not os.path.isdir(os.path.expanduser(os.environ['CHAMELEON_CACHE'])):
            cache_dir = os.path.abspath(os.path.join(cache_folder, 'chameleon_cache'))
            makedirs(cache_dir)
            os.environ['CHAMELEON_CACHE'] = cache_dir
        else:
            cache_dir = os.environ['CHAMELEON_CACHE']

        logger.debug("Configuring chamelean to cache at %s", cache_dir)
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

        template = component.getMultiAdapter((self, context),
                                             ITemplate,
                                             name=template)
        # context becomes the options/ dict.
        # We use self as the context so we can provide useful things
        # like the nikola site. It needs to be passed in the
        # The ViewPageTemplate likes to have a request
        context['context'] = self

        return template(self, request=Request(), **context)

    def inject_directory(self, directory):
        """Injects the directory with the lowest priority in the
        template search mechanism."""

        # This is called very early, that's the only reason that it gets
        # set low in the chains. It's called for each template plugin?
        self._provide_templates_from_directory(directory)


    def _provide_templates_from_directory(self, directory):
        if not isinstance(directory, str) and str is bytes:
            # nikola likes to provide these as unicode on Python 2,
            # which is incorrect (unless maybe on windows?)
            # Ideally we'd decode using the filesystem decoding or something,
            # right now we just assume the locale decodes right.
            directory = directory.encode("utf-8")

        directory = os.path.abspath(directory)
        theme_zcml = os.path.join(directory, 'theme.zcml')
        if os.path.exists(theme_zcml):
            xmlconfig.xmlconfig(theme_zcml)
        else:
            # Register macros for each macro found in each .macro.pt
            # file. This doesn't deal with naming conflicts.
            gsm = component.getGlobalSiteManager()
            for macro_file in glob.glob(os.path.join(directory, "*.macro.pt")):
                template = _ViewPageTemplateFileWithLoad(macro_file)
                for name in template.macros.names:
                    factory = MacroFactory(macro_file, name, 'text/html')
                    gsm.registerAdapter(factory,
                                        provided=(IMacroTemplate),
                                        required=(interface.Interface, interface.Interface,
                                                  interface.Interface),
                                        name=name)

            for template_file in glob.glob(os.path.join(directory, "*.tmpl.pt")):
                name = os.path.basename(template_file)
                name = name[:-len(".pt")]
                factory = TemplateFactory(template_file)
                # Register them as template adapters for us.
                gsm.registerAdapter(factory,
                                    provided=(ITemplate),
                                    required=(interface.Interface, interface.Interface),
                                    name=name)

                # Register them as views for traversing
                gsm.registerAdapter(SimpleViewClass(template_file, name=name),
                                    provided=interface.Interface,
                                    required=(interface.Interface, interface.Interface),
                                    name=name)
