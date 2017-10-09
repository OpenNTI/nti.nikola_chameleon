# -*- coding: utf-8 -*-
"""
Templating support for Chameleon under Nikola.

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

from nikola.utils import LocaleBorg

logger = __import__('logging').getLogger(__name__)

class NikolaPageFileTemplate(ViewPageTemplateFile):
    """
    ZPT file templates for use with Nikola.

    This does a few things:

    1. Sets up the ``load:`` expression to work.
    2. Restores the ``import:`` and ``structure:`` expression types.
    3. Provides a ``translate`` function based on Nikola's
       ``messages`` dictionary that will enable Chameleon's default
       I18N support.
    """
    # NOTE: We cannot do the rational thing and copy this
    # and modify our local value. This is because
    # certain packages, notably z3c.macro,
    # modify the superclass's value; depending on the order
    # of import, we may or may not get that change.
    # So we do the bad thing too and modify the superclass also

    @property
    def builtins(self):
        d = super(NikolaPageFileTemplate, self).builtins
        d['__loader'] = self._loader
        return d

    def _pt_get_context(self, instance, request, kwargs):     # pylint:disable=arguments-differ
        context = super(NikolaPageFileTemplate, self)._pt_get_context(
            instance, request, kwargs)
        # Set up translation
        context['translate'] = MessagesTranslate(kwargs['messages'])
        return context

    def render(self, target_language=None, **context):
        # We bypass BaseTemplate.render because it wants to setup
        # a bunch of translation stuff that's only applicable to
        # zope.i18n, and it overrides the translate function we pass
        # in which came from Nikola.
        assert 'request' in context
        assert 'translate' in context
        if target_language is None:
            target_language = LocaleBorg().current_lang

        context['target_language'] = target_language
        # pylint:disable=bad-super-call
        return super(BaseTemplate, self).render(**context)

BaseTemplate.expression_types['structure'] = PageTemplateFile.expression_types['structure']
BaseTemplate.expression_types['load'] = PageTemplateFile.expression_types['load']
BaseTemplate.expression_types['import'] = PageTemplateFile.expression_types['import']
z3c.macro.zcml.ViewPageTemplateFile = NikolaPageFileTemplate
zope.browserpage.simpleviewclass.ViewPageTemplateFile = NikolaPageFileTemplate


class TemplateFactory(object):

    def __init__(self, path):
        self.path = path
        # This object is known as "template" while the .pt
        # is running. We don't add anything to its dict to
        # allow us to share it, thus cutting down on the
        # running time.
        # Using z.p.p.PTF seems to disable caching.
        #self.template = zope.browserpage.viewpagetemplatefile.ViewPageTemplateFile(self.path)
        self.template = NikolaPageFileTemplate(self.path)

    def __call__(self, context, request):
        return self.template

# We also fix the namespaces in z3c.pt.namespaces to use the
# real namespace object.
# See https://github.com/zopefoundation/z3c.pt/issues/3
z3c.pt.namespaces.function_namespaces = zope.pagetemplate.engine.Engine.namespaces

class MessagesTranslate(object):
    """
    Implements the `translation function`_ for Chameleon
    in terms of the ``messages`` object provided by Nikola.

    The Nikola messages object is a dictionary from language to a dictionary
    of message ids to strings. Note that it doesn't support domains or
    mapping substitutions (mappings are included in the msgid as a
    format string, but nikola itself is expected to do the formatting).

    If it is called, it accepts the message id key as the first
    argument, and a 'lang' parameter as the optional second argument.
    If the lang is not given or is None, then it is defaulted to the
    "current language".

    .. versionadded:: 0.0.1a2

    .. _translation function: https://chameleon.readthedocs.io/en/latest/reference.html#translation-function
    """

    def __init__(self, messages):
        self._messages = messages

    def __call__(self, msgid, domain=None, mapping=None, context=None,
                 target_language=None, default=None):
        try:
            return self._messages(msgid, target_language)
        except KeyError:
            return default or msgid
