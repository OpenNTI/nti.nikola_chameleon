=================
 Getting Started
=================

.. note:: For the purposes of this document, the implementation of
          `Zope Page Templates
          <https://docs.zope.org/zope2/zope2book/AppendixC.html#define-define-variables>`_
          provided by `Chameleon
          <https://chameleon.readthedocs.io/>`_
          working together with `z3c.pt
          <https://pypi.python.org/pypi/z3c.pt>`_ will simply be
          referred to as "page templates" or abbreviated to "ZPT."

Introduction
============

This package allows developing Nikola templates using Chameleon.
Chameleon is a fast implementation of the Zope Page Templates
specification. Unlike template systems such as Jinja2 or Mako, page
templates are designed to be valid (X)HTML and may be edited in HTML
editors. It's even possible to use visual design tools to produce
pages that are then relatively easily turned into page templates;
sometimes it's even possible to edit those templates again in the same
visual design tool.

Component Architecture
======================

Page templates can be much more than that, though. When combined with
the Zope `component architecture
<https://zopecomponent.readthedocs.io/>`_ (ZCA), they can be designed
to be extensible and flexible in a way that the simple template
inheritance schemes of other template systems cannot match. This
package is designed to embrace that, making it possible to create and
extend templates and themes very easily.

.. note::

  Although we believe the component architecture can be used to make
  themes flexible and make changing and customizing them through
  inheritance or configuration easier, *you are not required to use
  these features* if you don't want to. You can build an entire theme
  just based on the files in the templates directory and the Chameleon
  ``load:`` expression.

For a discussion of how the ZCA can be leveraged in your themes, see :doc:`using_zca`.

Prerequisites
=============

To create templates with this package, you'll need a basic
understanding of the following:

- the page templates `language <https://chameleon.readthedocs.io/en/latest/reference.html>`_
- `path expressions
  <https://docs.zope.org/zope2/zope2book/AppendixC.html#tales-path-expressions>`_


It may be helpful to understand object traversal, similar to what can
be used in `the Pyramid web framework
<https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html>`_.


We use `zope.traversing
<https://pypi.python.org/pypi/zope.traversing>`_ to implement
traversal, and provide several "path adapters" and views to make
traversal in path expressions more convenient. For more information on
those helpers, see :doc:`path_helpers`.

Macros and Viewlets
-------------------

Most templates will also make use of `macros
<https://chameleon.readthedocs.io/en/latest/reference.html#macros-metal>`_,
and many will also use `viewlets
<https://pypi.python.org/pypi/zope.viewlet>`_. We'll discuss how each
of these can be used to develop flexible templates in :doc:`macros`
and :doc:`viewlets`, respectively. Complete examples using these
techniques can be found in `base-chameleon
<https://github.com/NextThought/nti.nikola_themes.base-chameleon>`_,
and its extension using bootstrap3, `bootstrap3-chameleon
<https://github.com/NextThought/nti.nikola_themes.bootstrap3-chameleon>`_.

Template Variables
==================

Your templates will have access to all of the `template variables
Nikola defines <https://getnikola.com/template-variables.html>`_.
These are made available in the ``options`` dictionary, one of `the
standard names
<https://docs.zope.org/zope2/zope2book/AppendixC.html#built-in-names>`_
available to page templates. The ``context`` standard name is often a
Nikola post object (or :ref:`other Nikola object <context-object>`),
and the context-specific template variables are available through it.
