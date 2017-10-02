# -*- coding: utf-8 -*-
"""
The Chameleon ZPT plugin for nikola.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports
import os
import os.path

from chameleon.zpt.template import PageTemplateFile
from nikola.plugin_categories import TemplateSystem
from nikola.utils import makedirs
import z3c.pt.pagetemplate
from zope.dottedname import resolve as dottedname

logger = __import__('logging').getLogger(__name__)

class _PageTemplateFileWithLoad(z3c.pt.pagetemplate.PageTemplateFile):
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
        d = super(_PageTemplateFileWithLoad, self).builtins
        d['__loader'] = self._loader
        return d

z3c.pt.pagetemplate.BaseTemplate.expression_types['load'] = PageTemplateFile.expression_types['load']


class ChameleonTemplates(TemplateSystem):

    name = 'nti.nikola_chameleon'


    def set_directories(self, directories, cache_folder):
        """Sets the list of folders where templates are located and cache."""
        # A list of directories where the templates will be
        # located. Most template systems have some sort of
        # template loading tool that can use this.

        # Does nothing, chameleon doesn't have the direct concept of a path,
        # only relative to the file with the load: expression.

        # We do set up the cache, though.

        cache_dir = None
        if  not 'CHAMELEON_CACHE' in os.environ or \
            not os.path.isdir(os.path.expanduser(os.environ['CHAMELEON_CACHE'])):
            os.environ['CHAMELEON_CACHE'] = cache_dir = os.path.join(cache_folder, 'chameleon_cache')
        else:
            cache_dir = os.environ['CHAMELEON_CACHE']

        logger.debug("Configuring chamelean to cache at %s", cache_dir)
        conf_mod = dottedname.resolve('chameleon.config')
        if conf_mod.CACHE_DIRECTORY != cache_dir:  # previously imported before we set the environment
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

    def render_template(self, template_name, output_name, context):
        """Renders template to a file using context.

        This must save the data to output_name *and* return it
        so that the caller may do additional processing.
        """
        result = self.render_template_to_string(template_name)
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
        template = _PageTemplateFileWithLoad(template)
        return template(**context)

    def inject_directory(self, directory):
        """Injects the directory with the lowest priority in the
        template search mechanism."""
        pass
