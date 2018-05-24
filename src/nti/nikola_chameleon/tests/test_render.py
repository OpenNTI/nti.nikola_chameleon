# -*- coding: utf-8 -*-
"""
Testing the entire rendering process.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from contextlib import contextmanager
import os
import unittest

from zope.component.testlayer import LayerBase
from zope.testing.cleanup import CleanUp

import nti.nikola_chameleon.tests
from nti.testing.layers import find_test

class RenderedLayer(CleanUp, LayerBase):

    def __init__(self):
        LayerBase.__init__(self, nti.nikola_chameleon.tests)
        self.testsite = os.path.join(os.path.dirname(__file__), 'testsite')
        self._rendered = False
        self.test = None

    @contextmanager
    def current_site_directory(self):
        cwd = os.getcwd()
        try:
            os.chdir(self.testsite)
            yield
        finally:
            os.chdir(cwd)

    def render(self):
        from nikola.__main__ import main
        from nikola import nikola
        with self.current_site_directory():
            # Make it raise exceptions instead of swallowing
            # them.
            old_debug = nikola.DEBUG
            nikola.DEBUG = True
            try:
                x = main(['build',
                          '--quiet', # TODO: Conditional on env variable
                          '--strict', '--no-continue', '-v2'])
                if x:
                    raise AssertionError("Build error", x)
            finally:
                nikola.DEBUG = old_debug
        self._rendered = True

    def testSetUp(self, test=None): # pylint:disable=arguments-differ
        self.test = test or find_test()

    def testTearDown(self):
        self.test = None

    def tearDown(self):
        import shutil

        with self.current_site_directory():
            if os.path.exists('output'):
                shutil.rmtree('output')
            # This gets different names under different versions
            # of python, for some reason.
            for pname in ('.doit.db.db', 'doit.db'):
                if os.path.exists(pname):
                    os.remove(pname)

        CleanUp.cleanUp(self)

    def _render_if_needed(self):
        if not self._rendered:
            self.render()

    def assertOutputExists(self, *path):
        self._render_if_needed()
        fname = os.path.join(self.testsite, 'output', *path)
        if not os.path.isfile(fname):
            self.test.fail("No path %s" % (fname,)) # pragma: no cover
        return fname

    def assertInOutput(self, expected, *path):
        self._render_if_needed()
        fname = self.assertOutputExists(*path)
        with open(fname, 'r') as f:
            actual = f.read()

        self.test.assertIn(expected, actual)

LAYER = RenderedLayer()


class TestRender(unittest.TestCase):

    layer = LAYER

    def test_render(self):
        self.layer.assertOutputExists("index.html")
        self.layer.assertOutputExists("index.atom")
        self.layer.assertOutputExists("rss.xml")
        self.layer.assertOutputExists("pages", "about-nikola.html")
        self.layer.assertOutputExists("listings", "index.html")
        self.layer.assertOutputExists("listings", "hello.py.html")

        self.layer.assertInOutput('<div class="metadata"><p class="feedlink">',
                                  'authors', 'jason-madden.html')
        self.layer.assertInOutput('<li class="post-list-item">',
                                  "pages", 'post-list-test.html')
        self.layer.assertInOutput('<a href="../posts/welcome-to-nikola.html">Welcome to Nikola</a>',
                                  "pages", 'post-list-test.html')

        self.layer.assertOutputExists('posts', 'test-page.html')
        self.layer.assertInOutput("<div>This came from a shortcode</div>",
                                  'posts', 'test-page.html')
