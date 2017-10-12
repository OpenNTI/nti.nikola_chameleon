=========
 Details
=========

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

Page templates can be much more than that, though. When combined with
the Zope `component architecture
<https://zopecomponent.readthedocs.io/>`_, they can be designed to be
extensible and flexible in a way that the simple template inheritance
schemes of other template systems cannot match. This package is
designed to embrace that, making it possible to create and extend
templates and themes very easily.

To create templates with this package, you'll need a basic
understanding of the following:

- the page templates `language <https://chameleon.readthedocs.io/en/latest/reference.html>`_
- `path expressions
  <https://docs.zope.org/zope2/zope2book/AppendixC.html#tales-path-expressions>`_

Most templates will also make use of `macros
<https://chameleon.readthedocs.io/en/latest/reference.html#macros-metal>`_,
and many will also use `viewlets
<https://pypi.python.org/pypi/zope.viewlet>`_. We'll discuss how each
of these can be used to develop flexible templates. Complete examples using
these techniques can be found  in `base-chameleon
<https://github.com/NextThought/nti.nikola_themes.base-chameleon>`_,
and its extension using bootstrap3,
`bootstrap3-chameleon
<https://github.com/NextThought/nti.nikola_themes.bootstrap3-chameleon>`_.

Theory of Operation
===================

Talk about component lookup: context, request/layer, view and how we
can register macros and viewlets for each of those things.

Talk about what each represents.

Using Macros
============

- Using macros from the same template: template/macros/macro_name
- Using defined templates: macro:macro_name
  - Automatically discovered in .macro.pt files for any triple.
  - Registered from ZCML for specific triples.

Using Viewlets
==============

- The provider:viewlet_manager expression
- Registered in ZCML
- Standard viewlet manager types.

- TODO: Adding viewlet managers?
