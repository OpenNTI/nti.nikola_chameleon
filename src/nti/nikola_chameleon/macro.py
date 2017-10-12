# -*- coding: utf-8 -*-
"""
Supporting code for z3c.macro.

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
    """
    Provides a generic ``@@macros`` view for finding a z3c.macro registration
    on a context *different* than the current context.

    The object that it was traversed from will become the ``context`` variable
    during executing of the macro. E.g., in ``metal:use-macro="post/@@macros/a_macro"``, the
    registered macro ``a_macro`` will be looked up with ``post`` as its context and will
    execute with ``post`` as its ``context`` variable.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        view = self.request.options['view']
        templates = view.templates
        return BoundMacro(self.context,
                          get_macro_template(self.context,
                                             templates.new_view_for_context(self.context,
                                                                            self.request),
                                             self.request,
                                             name))
