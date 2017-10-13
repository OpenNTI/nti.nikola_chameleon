# -*- coding: utf-8 -*-
"""
Testing the entire rendering process.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import unittest

from zope.testing.cleanup import CleanUp

class TestRender(CleanUp,unittest.TestCase):

    def test_render(self):
        from nikola.__main__ import main
        import os
        import shutil
        cwd = os.getcwd()
        testsite = os.path.join(os.path.dirname(__file__), 'testsite')
        os.chdir(testsite)
        self.addCleanup(os.chdir, cwd)

        main(['build', '-q'])

        shutil.rmtree('output')
        # This gets different names under different versions
        # of python, for some reason.
        if os.path.exists('.doit.db.db'): # python 3
            os.remove('.doit.db.db')
        else:
            os.remove(".doit.db")
