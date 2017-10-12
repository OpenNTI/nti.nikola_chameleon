# -*- coding: utf-8 -*-
"""
Adapters for various object types.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from zope import component
from zope import interface
from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import IPathAdapter

from .interfaces import IPost

@interface.implementer(IPathAdapter, ITraversable)
@component.adapter(IPost)
class MetaPathAdapter(object):
    """
    Lets us access the meta object in path
    expressions.

    ``post/meta:link`` ``post/meta:keywords``
    """

    def __init__(self, context):
        self.context = context

    def traverse(self, name, furtherPath):
        return self.context.meta(name)


@interface.implementer(IPathAdapter, ITraversable)
@component.adapter(IPost)
class FormattedDatePathAdapter(object):
    """
    Lets us access the formatted date function
    in tales expressions.

    ``post/formatted_date:webiso`` ``post/formatted_date:?date_format``

    .. versionadded:: 0.0.1a2
    """

    def __init__(self, context):
        self.context = context

    def traverse(self, name, furtherPath):
        return self.context.formatted_date(name)
