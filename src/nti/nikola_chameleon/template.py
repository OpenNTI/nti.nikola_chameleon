# -*- coding: utf-8 -*-
"""
The Chameleon ZPT plugin for nikola.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from chameleon.zpt.template import PageTemplateFile
import z3c.macro.zcml
from z3c.pt.pagetemplate import ViewPageTemplateFile
from z3c.pt.pagetemplate import BaseTemplate
import z3c.pt.namespaces
import zope.pagetemplate.engine
import zope.browserpage.simpleviewclass
import zope.browserpage.viewpagetemplatefile
import zope.pagetemplate.pagetemplatefile

logger = __import__('logging').getLogger(__name__)

class ViewPageTemplateFileWithLoad(ViewPageTemplateFile):
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
        d = super(ViewPageTemplateFileWithLoad, self).builtins
        d['__loader'] = self._loader
        return d

BaseTemplate.expression_types['structure'] = PageTemplateFile.expression_types['structure']
BaseTemplate.expression_types['load'] = PageTemplateFile.expression_types['load']
z3c.macro.zcml.ViewPageTemplateFile = ViewPageTemplateFileWithLoad
zope.browserpage.simpleviewclass.ViewPageTemplateFile = ViewPageTemplateFileWithLoad


class TemplateFactory(object):

    def __init__(self, path):
        self.path = path
        # This object is known as "template" while the .pt
        # is running. We don't add anything to its dict to
        # allow us to share it, thus cutting down on the
        # running time.
        # Using z.p.p.PTF seems to disable caching.
        #self.template = zope.browserpage.viewpagetemplatefile.ViewPageTemplateFile(self.path)
        self.template = ViewPageTemplateFileWithLoad(self.path)

    def __call__(self, context, request):
        return self.template

# We also fix the namespaces in z3c.pt.namespaces to use the
# real namespace object.
# See https://github.com/zopefoundation/z3c.pt/issues/3
z3c.pt.namespaces.function_namespaces = zope.pagetemplate.engine.Engine.namespaces
