# -*- coding: utf-8 -*-
"""
View objects.

These objects will typically provide chunks of functionality that are
ugly to write and/or test in templates. They will be registered in
ZCML against specific (context, request) pairs (as specific as
needed). They (and their attributes, methods and templates) can then
be easily accessed in a template by traversal:
``context/@@view_name/method``.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from zope import interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.viewlet.manager import ConditionalViewletManager as ZConditionalViewletManager

from . import interfaces

@interface.implementer(IBrowserView)
class BaseView(object):
    """
    All views provide the ``context`` and ``request`` attributes.
    """

    context = None
    request = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

class View(BaseView):
    """
    The default view when we begin rendering a template.

    It may have "layers" applied to it to adjust the
    rendering conditions.
    """

    #: The :class:`~.ChameleonTemplates` instance that
    #: is running the rendering process. You have access
    #: to the nikola site through the ``site`` object.
    templates = None

    def __init__(self, context, request, templates):
        BaseView.__init__(self, context, request)
        self.templates = templates

class PostTextView(BaseView):
    """
    For getting the text of a post, while respecting teasers.

    .. versionadded:: 0.0.1a2
    """

    @property
    def teaser(self):
        """
        The string 'teaser' if the content is a teaser in an index, otherwise
        None.
        """
        return 'teaser' if self.request.options['index_teasers'] else None

    @property
    def content_kind(self):
        """
        Either 'summary' or 'content'. Intended to be used in
        CSS class names in indices.
        """
        return 'summary' if self.teaser else 'content'


    @property
    def content(self):
        """
        The full text or teaser text of the post, as appropriate, in
        an index.
        """
        return self.context.text(teaser_only=bool(self.teaser))

    @property
    def preview(self):
        """
        The string 'post-preview' if the content is a teaser.
        """
        return 'post-preview' if self.teaser else ''

    @property
    def embedded_content(self):
        """
        The teaser for a post, stripped of html. Works regardless of index
        status.
        """
        return self.context.text(teaser_only=True, strip_html=True)

class PostCssKindView(BaseView):
    """
    For getting various strings useful in CSS.

    .. versionadded:: 0.0.1a3
    """

    @property
    def pagekind_class(self):
        """
        Returns a class name suitable for use in CSS.
        """
        layer = self.request
        providing = list(interface.providedBy(layer).flattened())
        for p in providing:
            if p.isOrExtends(interfaces.IPageKind):
                name = p.__name__[1:-4].lower()
                return name

class ConditionalViewletManager(ZConditionalViewletManager):
    """
    A viewlet manager that respects the ``weight`` and ``available``
    attributes.
    """
