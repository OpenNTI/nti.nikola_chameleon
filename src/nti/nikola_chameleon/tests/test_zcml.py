# -*- coding: utf-8 -*-
"""
Tests for zcml.py

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import unittest

from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import is_not as does_not

from zope.configuration import xmlconfig
from zope.testing.cleanup import CleanUp

from .. import viewlets

class TestZCML(CleanUp,
               unittest.TestCase):

    def test_registers_interface(self):
        zcml = """
        <configure xmlns="http://namespaces.zope.org/zope"
                   xmlns:browser="http://namespaces.zope.org/browser">
          <include package="nti.nikola_chameleon" file="meta.zcml" />
          <browser:newViewletManager
              id="ILeftColumn" />
        </configure>
        """

        xmlconfig.string(zcml)

        assert_that(viewlets, has_property('ILeftColumn'))

    def test_viewlet_manager_in_same_zcml(self):
        assert_that(viewlets, does_not(has_property('ILeftColumn')))
        zcml = """
        <configure xmlns="http://namespaces.zope.org/zope"
                   xmlns:browser="http://namespaces.zope.org/browser">
          <include package="nti.nikola_chameleon" file="meta.zcml" />
          <include package="zope.viewlet" file="meta.zcml" />
          <browser:newViewletManager
              id="ILeftColumn" />
          <browser:viewletManager
              name="left_column"
              provides="nti.nikola_chameleon.viewlets.ILeftColumn"
              permission="zope.Public" />
        </configure>
        """

        xmlconfig.string(zcml)
        assert_that(viewlets, has_property('ILeftColumn'))

        context = object()
        from zope.publisher.browser import TestRequest
        request = TestRequest()
        from zope.publisher.browser import BrowserView
        view = BrowserView(context, request)

        import zope.component
        from zope.viewlet import interfaces
        zope.component.getMultiAdapter(
            (context, request, view),
            interfaces.IViewletManager,
            name='left_column')

        zope.component.getMultiAdapter(
            (context, request, view),
            viewlets.ILeftColumn,
            name='left_column')
