=====================
 nti.nikola_chameleon
=====================

.. image:: https://img.shields.io/pypi/v/nti.nikola_chameleon.svg
        :target: https://pypi.python.org/pypi/nti.nikola_chameleon/
        :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/nti.nikola_chameleon.svg
        :target: https://pypi.org/project/nti.nikola_chameleon/
        :alt: Supported Python versions

.. image:: https://travis-ci.org/NextThought/nti.nikola_chameleon.svg?branch=master
        :target: https://travis-ci.org/NextThought/nti.nikola_chameleon

.. image:: https://coveralls.io/repos/github/NextThought/nti.nikola_chameleon/badge.svg?branch=master
        :target: https://coveralls.io/github/NextThought/nti.nikola_chameleon?branch=master

..
  .. image:: https://readthedocs.org/projects/ntinikola_chameleon/badge/?version=latest
        :target: https://ntinikola_chameleon.readthedocs.io/en/latest/
        :alt: Documentation Status

A template system for the `Nikola
<https://pypi.python.org/pypi/Nikola>`_ static blog system using
`Chameleon <https://pypi.python.org/pypi/Chameleon>`_ and `z3c.pt
<https://pypi.python.org/pypi/z3c.pt>`_.

Nikola uses a `custom mechanism <https://pypi.python.org/pypi/yapsy>`_
to find plugins instead of using the usual ``pkg_resources`` system.
That makes it *incredibly* difficult to install plugins; it's not enough
just to ``pip install`` a package from PyPI. Instead, you must *also*
copy a ``.plugin`` file to a particular location on disk. This can be:

- ~/.nikola/plugins/
- The ``plugins`` directory of your Nikola site.

Beside that '.plugin' file there must also be a '.py' file of the same
name that the plugin lists as a module (yes, even though the plugin file
specifically requests a Python module, yapsy requires that it be a
file or directory beside the plugin file---so not really a module).

It's ridiculous to require everyone to copy plugins into their plugin
folder (they're not even correctly on sys.path, meaning that
zope.configuration and many other tools won't work) and we don't plan
to let Nikola do that automatically (we're not on the Nikola plugin
index and won't be until they let us do standard installs), so the
best we can do is attempt to workaround yapsy's limitations.

Into your site's plugin directory, place the following .py file::

  # nti_nikola_chameleon.py
  from nti.nikola_chameleon import *


..
  Rendering the plugin file must be last, it is done by
  setup.py (since PyPI does not support the ..include directive.)

Beside that, you'll need a ``nti.nikola_chameleon.plugin`` file::
