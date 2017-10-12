# -*- coding: utf-8 -*-
"""
Request objects.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports

from zope import interface

from zope.publisher.interfaces.browser import IDefaultBrowserLayer


logger = __import__('logging').getLogger(__name__)

class Response(object):

    def getHeader(self, name): # response
        return 'text/html'

@interface.implementer(IDefaultBrowserLayer)
class Request(object):
    # Minimum request-like object to use when rendering
    # We claim to implement zope.publisher's IRequest in order to
    # be able to use all the pre-registered adapters.
    response = Response()
    context = None
    debug = False

    def __init__(self, context, options):
        # The options dictionary in the templates, AKA
        # the 'context' argument to render_template.
        self.context = context
        self.options = options
