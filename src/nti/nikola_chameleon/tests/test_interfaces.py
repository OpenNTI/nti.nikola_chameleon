# -*- coding: utf-8 -*-
"""
Tests for interfaces.py

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports
import unittest

from nti.testing.matchers import implements

from hamcrest import assert_that
from hamcrest import has_entry

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904



class TestInterfaces(unittest.TestCase):

    @property
    def _FUT(self):
        from nti.nikola_chameleon import interfaces
        return interfaces

    def test_post_implements(self):
        from nikola.post import Post
        assert_that(Post, implements(self._FUT.IPost))

    def test_story_page_kind(self):
        interfaces = self._FUT
        assert_that(interfaces.PAGEKINDS,
                    has_entry(frozenset(('page_page', 'story_page')),
                              interfaces.IStoryPageKind))
