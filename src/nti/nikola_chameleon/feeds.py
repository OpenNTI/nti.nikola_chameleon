# -*- coding: utf-8 -*-
"""
The Chameleon ZPT plugin for nikola.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports

from z3c.pt.pagetemplate import ViewPageTemplate
from zope import interface

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.viewlet import ViewletBase

from .view import BaseView

@interface.implementer(IDefaultBrowserLayer)
class Feeds(BaseView):
    "Helpers for feeds."
    # These are in feeds_translations.tmpl in mako.
    # They can and should be decomposed more so that the parameters
    # are based on configuration, context, view, layer.

    @property
    def options(self):
        return self.request.options

    _head_feed_link_tmpl = ViewPageTemplate("""
    <link tal:define="_link nocall:options/_link"
          rel="alternate" type="${options/link_type}"
          title="${options/link_name}" hreflang="${options/language}"
          href="${python:_link(options['kind'] + '_' + options['link_postfix'], options['classification'], options['language'])}">
    """)

    def _head_feed_link(self, link_type, link_name, link_postfix, classification, kind, language):
        if len(self.options['translations']) > 1:
            raise NotImplementedError("Translations not supported")

        context = dict(self.options)
        context.update(locals())
        context.pop('self')
        # Bind the old 'view' object (really a ChameleonTemplates)
        # to view again.
        return self._head_feed_link_tmpl(request=self.request, **context)

    def _feed_head_rss(self, classification=None, kind='index', rss_override=True):
        options = self.options
        result = u''
        if options['rss_link'] and rss_override:
            result = options['rss_link']

        if (options['generate_rss']
                and not (options['rss_link'] and rss_override)
                and kind != 'archive'):
            if len(options['translations']) > 1:
                raise NotImplementedError("Translations not supported")
            for language in sorted(options['translations']):
                if (classification or classification == '') and kind != 'index':
                    result += self._head_feed_link(
                        'application/rss+xml',
                        'RSS for ' + kind + ' ' + classification,
                        'rss',
                        classification,
                        kind,
                        language)
                else:
                    result += self._head_feed_link('application/rss+xml',
                                                   'RSS',
                                                   'rss',
                                                   classification,
                                                   'index',
                                                   language)
        return result

    def _feed_head_atom(self, classification=None, kind='index'):
        result = u''
        if self.options['generate_atom']:
            for language in sorted(self.options['translations']):
                if (classification or classification == '') and kind != 'index':
                    result += self._head_feed_link(
                        'application/atom+xml',
                        'Atom for ' + kind + ' ' + classification, 'atom',
                        classification,
                        kind,
                        language)
                else:
                    result += self._head_feed_link('application/atom+xml', 'Atom', 'atom',
                                                   classification, 'index', language)
        return result

    def feed_translations_head(self, classification=None, kind='index',
                               feeds=True, other=True, rss_override=True,
                               has_no_feeds=False):
        "Produce the links in the head."
        result = u''
        if kind is None:
            kind = 'index'
        if feeds and not has_no_feeds:
            result = self._feed_head_rss(classification,
                                         'index' if (kind == 'archive' and rss_override) else kind,
                                         rss_override)
            result += self._feed_head_atom(classification, kind)
        # elide support for translations
        return result


class HTMLFeedLinkViewlet(ViewletBase):
    """
    A viewlet to render one or more feed links into html.

    You must subclass this to set the name of the classification
    attribute to find in the request options dictionary in the
    ``classification_name`` attribute. This is usually done in ZCML::

       <browser:viewlet
          name="feed_content_header"
          manager=".interfaces.IHtmlBodyContentHeaderViewletManager"
          class=".feeds.HTMLFeedLinkViewlet"
          layer=".interfaces.IAuthorPageKind"
          permission="zope.Public"
          weight="1"
          classification_name="author"
          />
    """
    available = False
    classification_name = None

    def __init__(self, context, request, view, manager):
        # There's a bug in the viewlet manager: it filters
        # before doing the update(), so you can't set
        # 'available' in update.
        super(HTMLFeedLinkViewlet, self).__init__(context, request, view, manager)
        self.update()

    def update(self):
        options = self.request.options
        generate_atom = options['generate_atom']
        generate_rss = options['generate_rss']

        if generate_atom or generate_rss:
            self.available = True

    _html_feed_link_tmpl = ViewPageTemplate("""
    <a tal:define="_link nocall:options/_link;
                   messages nocall:options/messages;
                   language options/language;
                   link_name options/link_name;"
          type="${options/link_type}"
          title="${link_name}" hreflang="${language}"
          href="${python:_link(options['kind'] + '_' + options['link_postfix'], options['classification'], language)}"
    >
    ${python:messages(link_name, language)}${options/extra}
    </a>
    """)

    def _html_feed_link(self, link_type, link_name, link_postfix, classification, kind, language,
                        name=None):
        # Elide translations
        context = dict(self.request.options)
        context.update(locals())
        context.pop('self')

        extra = u''
        if name and kind != "archive" and kind != "author":
            extra = " (" + name + ")"
        # Bind the old 'view' object (really a ChameleonTemplates)
        # to view again.
        return self._html_feed_link_tmpl(request=self.request, extra=extra, **context)


    def render(self):
        options = self.request.options
        classification = options[self.classification_name]
        kind = options['kind']
        generate_atom = options['generate_atom']
        generate_rss = options['generate_rss']
        translations = options['translations']
        # Elide translations
        strs = []
        for language in sorted(translations):
            strs.append('<div class="metadata"><p class="feedlink">')
            if generate_atom:
                strs.append(self._html_feed_link('application/atom+xml',
                                                 'Atom feed',
                                                 'atom',
                                                 classification, kind, language))

            if generate_rss and kind != 'archive':
                strs.append(self._html_feed_link('application/rss+xml',
                                                 'RSS feed',
                                                 'rss',
                                                 classification, kind, language))

            strs.append("</p></div>")
        result = '\n'.join(strs)
        return result
