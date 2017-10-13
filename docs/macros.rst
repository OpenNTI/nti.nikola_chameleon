==============
 Using Macros
==============

.. highlight:: html

`Macros
<https://chameleon.readthedocs.io/en/latest/reference.html#macros-metal>`_,
are a simple way to create re-usable snippets of templates. They can
be used as-is, or they can be lightly customized at the point of use
by `filling slots <https://chameleon.readthedocs.io/en/latest/reference.html#id40>`_.

This document will cover the ways in which macros can be used in
Nikola themes created with this package; it will generally assume that you
already understand the basics of creating and using macros on Chameleon.

One important thing to point out: the value of a ``use-macro``
attribute is a true *expression*. It is evaluated to find the macro
object. It's not just a simple name. This allows most of the scenarios
we will discuss below.

Using Macros From the Same Template
===================================

While not particularly common, it is possible to create and use macros
all within the scope of a single template. One of `the standard names
<https://docs.zope.org/zope2/zope2book/AppendixC.html#built-in-names>`_
defined for path expressions is ``template`` referring to the
currently executing template. A Chameleon template has a ``macros``
dictionary that lists all the macros defined within by name.
Therefore, to use a macro from the same template, we would write an
expression like ``template/macros/macro_name`` (here, in a file called
``hello.tmpl.pt``)::

  <html>

    <p metal:define-macro="hello">
        Hello <p metal:define-slot="name">world</p>
    </p>

    <body>

      <p tal:repeat="post context/posts"
         metal:use-macro="template/macros/hello">
         <p metal:fill-slot="name">${post/author}</p>
     </p>

    </body>

  </html>

Using Macros From Other Templates
=================================

When a template defines macros, they can be used from other templates
as well. The key is that ``use-macro`` takes an expression; we just
have to provide an expression that evaluates to a macro.

Load Expressions
----------------

The simplest (but least flexible) way to do this is with Chameleon's
built-in ``load:`` expression. This will load a template in from a file
relative to the current file. If the ``hello`` macro from the previous
section was defined in ``hello.tmpl.pt``, the file ``index.tmpl.pt`` could use
it like this::

    <html>
      <body tal:define="hello-template load:hello.tmpl.pt">
        <p tal:repeat="post context/posts"
           metal:use-macro="hello-template/macros/hello">
         <p metal:fill-slot="name">${post/author}</p>
        </p>
      </body>
    </html>

Flexibility Through the Component Architecture
----------------------------------------------

Far more flexible is to make use of :doc:`the component architecture
<using_zca>`. We can do this in a few ways. One is to rely on the fact
that :ref:`views are automatically registered for each .tmpl.pt
<auto-register-template-views>` found in the theme's ``templates``
directory. Each such view will have an ``index`` attribute that is a
template, and which in turn will have the ``macros`` dictionary. We
could change ``index.tmpl.pt`` to use this view::

    <html>
      <body>
        <p tal:repeat="post context/posts"
           metal:use-macro="context/@@hello.tmpl/index/macros/hello">
         <p metal:fill-slot="name">${post/author}</p>
        </p>
      </body>
    </html>

How is this more flexible? Isn't that just another way to refer to
a file?

This is more flexible for two reasons. The first is that a theme that
extends us (see :doc:`inheritance`) could provide its *own*
``hello.tmpl`` view (maybe defining different CSS classes or using
``<div>`` instead of ``<p>``) and we would automatically use it. The
second (and similar) reason is that the traversal through ``context``
gives the component architecture a chance to define a more specific
view for that particular type of :ref:`context <context-object>`. (Of
course we could traverse through *any* object and potentially locate a
more specific view for that object.) This lets us (or themes that
extend us) do something like use a generic macro for most types of
objects, but also provide a custom macro that automatically gets used
for galleries or slides. All without having to change the base
template!

``macro:`` Expressions
~~~~~~~~~~~~~~~~~~~~~~

An even more powerful and flexible way to locate macros is with the
`z3c.macro <https://pypi.python.org/pypi/z3c.macro>`_ ``macro:``
expression type. Unlike all of the above approaches, this abstracts
the notion of a macro away from its location (we don't have to think
about what file or view the macro is defined in). Instead, we just
use the macro's name: ``<p metal:use-macro="macro:hello" />``.

At first this may seem *less* flexible: at least with traversal we got
to choose a variable to traverse through and could register macros for
particular context objects. But the macro expression actually
automatically searches for the macro based on all three of the
context, request, and view. That gives us the same three degrees of
freedom to define custom macros for particular types of context
objects, pages and comment systems that we have :ref:`for templates
<lookup-templates>`.

All macros found in ``*.macro.pt`` files are :ref:`automatically
registered <auto-register-macros>` for the lest specific, most generic
interfaces possible. You can easily :ref:`add your own macros in ZCML
<lookup-macros>` for more specific registrations.

Finding Macros For a Different Context
++++++++++++++++++++++++++++++++++++++

The ``macro:`` expression always looks up its target based on the
current context, request and view. Sometimes, particularly when
working with the contents of a container---such as the posts in an
index---you want to look up a macro with a different context (the
object in the container). The :ref:`@@macros view <macros-view>` lets
you do this::

    <html>
      <body>
        <p tal:repeat="post context/posts">
         <p metal:use-macro="post/@@macros/display">Display a post.</p>
        </p>
      </body>
    </html>


The ``template`` Variable and Macros
------------------------------------

One useful quirk involves the ``template`` variable: When you use a
macro from another file, no matter how you got it, whether from a load
expression or the component architecture, while that macro is
executing, ``template`` still refers to the file that called it! This
is yet another way of overriding bits and pieces of macros if macros
are looked up from the ``template`` variable; of course it does
introduce fairly tight coupling between the files.

Suppose we have ``page.tmpl.pt`` for ordinary (non blog-post) pages::

  <html>
    <header metal:define-macro="header">
        <h1>${context/title}</h1>
        <div class="metadata"
             metal:use-macro="template/macros/metadata">
          Put the metadata here
        </div>
    </header>
    <div metal:define-macro="metadata">
      <!--! Pages don't have any metadata -->
    </div>
    <body>
        <article>
          <header metal:use-macro="template/macros/header">
          </header>
          ...
        </article>
    </body>
  </html>

Now, ``post.tmpl.pt`` could use the ``header`` macro from
``page.tmpl.pt`` and still fill in its own ``metadata`` macro::

  <html>
    <div metal:define-macro="metadata">
        <h1>Author: ${context/author}</h1>
    </div>
    <body>
        <article>
          <header metal:use-macro="context/@@page.tmpl/index/macros/header">
          </header>
          ...
        </article>
    </body>
  </html>


This is similar to filling slots, but works with any level of nesting.


Macro Limitations and Challenges
================================

- Macros always expand to exactly one piece of content (content for a
  macro cannot come from multiple places).
- Slots can be difficult to use effectively through multiple levels of
  nesting.
- The macro namespace is flat.

Some of these challenges are addressed with :doc:`viewlets <viewlets>`.
