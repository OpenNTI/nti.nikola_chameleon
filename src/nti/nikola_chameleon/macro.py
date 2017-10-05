# -*- coding: utf-8 -*-
"""
The Chameleon ZPT plugin for nikola.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from z3c.macro.tales import get_macro_template

from zope import interface

from zope.traversing.interfaces import ITraversable


class BoundMacro(object):

    def __init__(self, context, func):
        self.context = context
        self.func = func

    def include(self, stream, econtext, *args, **kwargs):
        # This is a copy
        econtext['context'] = self.context
        return self.func.include(stream, econtext, *args, **kwargs)

@interface.implementer(ITraversable)
class NamedMacroView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        return BoundMacro(self.context,
                          get_macro_template(self.context, None, self.request, name))
