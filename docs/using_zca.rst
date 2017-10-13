=======================================
 Leveraging the Component Architecture
=======================================

.. highlight:: xml
.. currentmodule:: nti.nikola_chameleon.interfaces

Background
==========

If you're not familiar with component architectures, and
``zope.component`` in particular, please take a few minutes to read
:doc:`zca_background`.


Key Objects
===========

Three of the `the standard names
<https://docs.zope.org/zope2/zope2book/AppendixC.html#built-in-names>`_
available in templates play a particularly important part in the way
templates, macros and viewlets are used.

Those names are ``context``, ``request`` and ``view``. These names are
inherited from the Zope family of Web frameworks, but they have equal
relevance here. We'll begin by discussing each of the objects
individually, and then in :ref:`lookup` we will explore how they come
together.

.. _context-object:

Context
-------

The *context* is the object being rendered. It is most commonly a Nikola
post (represented by :class:`IPost`),
but it can also be a
:class:`IPostList` on index pages, or
:class:`~IGallery`,
:class:`~IListing`
or :class:`~ISlide` on their
respective pages.

.. tip:: The `template variables
         <https://getnikola.com/template-variables.html>`_ for
         specific template pages are available from the ``context``
         object, in addition to being available from the ``options``
         dictionary. Using ``context`` can result templates that are
         more clear in their intent.

Request
-------

The *request* (also known as the *layer* for the role it plays)
expresses the intent of the render. It tells us the purpose of our
rendering. It will always provide the
:class:`~IPageKind` interface. Indeed,
it will actually always provide one of the more specific interfaces
that better identifies what we're trying to render, such as
:class:`~ITagsPageKind`.

In the Zope web framework, various interfaces are applied to
the request to determine the "skin", or appearance, of web
pages. Layers are also used to determine available
functionality such as the contents of menus. ``IPageKind`` is used for
similar purposes.

View
----

Finally, the *view* is the code that initiated the rendering. In the
web frameworks, this typically corresponds to the last portion of the
URL. It determines the overall output by choosing the template to
render and providing additional functionality. For example, if the
context is a JPEG photograph, a URL like ``/photo.jpg/full_screen``
may use a view called ``full_screen`` and result in a full-screen view
of the photograph, while for the same photo, a URL like
``/photo.jpg/thumbnail`` may produce a small thumbnail using a view
called ``thumbnail``

In Nikola, it is always the Nikola engine that initiated the rendering
process, and so the view object is always the same, an instance of
:class:`~nti.nikola_chameleon.view.View`. This object provides a
``templates`` attribute to access the
:class:`~nti.nikola_chameleon.plugin.ChameleonTemplates` object,
through which the Nikola site object can be found.

In addition, the view also has "layer" interfaces applied to it to
express various aspects of system configuration. Currently the only
such layer is the
:class:`~ICommentKind`. More
specifically, a particular subinterface identifying whether comments
are disabled (:class:`~ICommentKindNone`) or enabled
(:class:`ICommentKindAllowed`) and if they are enabled what specific
comment system is being used (:class:`ICommentKindDisqus`).


.. caution::

   The specific layer interfaces applied to requests and
   views are subject to change in future versions. The division now is
   somewhat arbitrary, but the intent is to allow for registering
   macros for a request layer of :class:`IStoryPageKind` when comments
   are :class:`ICommentKindDisqus`; to do that we need to be able to
   separate those interfaces on different objects, or introduce a
   bunch of unified interfaces (``IStoryPageKindCommendKindDisqus``),
   which is intractable.

.. _lookup:

Component Lookup
================

Now that we know about the three key objects, we can talk about
exactly why they are so key and how they are used. In short, they are
used for component lookup through the system, and it is this layer of
indirection that permits us flexibility and allows for easy
:doc:`inheritance`. Or to put it more pragmatically, they allow us to
*declaratively configure* how templates are composed and used, instead
of creating a `mess of spaghetti code
<https://getnikola.com/theming.html#identifying-and-customizing-different-kinds-of-pages-with-a-shared-template>`_.

Throughout, we will use the example of Nikola rendering a page (not a
blog post) in a system that has Disqus comments enabled.

.. _lookup-templates:

Templates
---------

Let's begin at the beginning. When Nikola asks to find a template, say
``page.tmpl``, we begin by determining the correct ``context``,
``request`` and ``view`` to use, applying the appropriate layers to
each object.

At this point we have a ``context`` implementing :class:`IPost`, a
``request`` implementing :class:`IPostPageKind`, and a ``view``
implementing :class:`ICommentKindDisqus`.

These three objects *together* are used to :func:`ask the component
registry for an adapter <nti.nikola_chameleon.plugin.getViewTemplate>`
to ``IContentTemplate``. This means that, in addition to the name, we
have three degrees of freedom for finding a template. This is a great
way to keep programattic logic out of your templates, streamlining
them, reducing the chances of error, and shifting runtime checks to
faster declarative configuration.

:ref:`By default <auto-register-templates>`, if a ``page.tmpl.pt``
file exists on disk, it will be found registered for the ``page.tmpl``
template name. All such default templates are registered with the
lowest priority, least-specific interfaces possible. This means that
you can easily provide a more specific template customized exactly for
pages that have disqus comments enabled.

In your :ref:`theme.zcml <zcml>`, you would include a `z3c.template
<https://pypi.python.org/pypi/z3c.template#context-specific-template>`_
directive to register this template. (We'll say that this custom
template file is named ``disqus_page.pt.`` Remember that the template
we're replacing, the one Nikola is asking for, is named ``page.tmpl``)

::

  <configure  xmlns="http://namespaces.zope.org/zope"
              xmlns:i18n="http://namespaces.zope.org/i18n"
              xmlns:zcml="http://namespaces.zope.org/zcml"
              xmlns:z3c="http://namespaces.zope.org/z3c"
              xmlns:browser="http://namespaces.zope.org/browser"
              >
    <include package="z3c.template" file="meta.zcml" />

    <z3c:template
       template="disqus_page.pt"
       name="page.tmpl"
       context=".interfaces.IPost"
       layer=".interfaces.IPostPageKind"
       for=".interfaces.ICommentKindDisqus"
       />

  </configure>


.. note:: In the ``z3c:template`` directive, ``layer`` means the
          request object, and ``for`` means the view object.

Although this is certainly possible, and may work well for extremely
special cases, or for keeping your .pt files as full HTML that can be
edited in a visual editor, replacing an entire template like this is
rare, though. There are more effective ways to control the content on
portions of a page with macros and viewlets.

Adding Templates
~~~~~~~~~~~~~~~~

Another way to use this lookup of templates in the component registry
is to add templates that don't exist on disk (and hence wouldn't be
registered by default). This is useful when templates are similar
enough that they can be collapsed into a single file, with all of what
needs to be different between them managed by macros and viewlets
registered for specific interfaces. The other templating systems
Nikola supports don't have this flexibility, so Nikola asks for a
different template name in almost every situation; we can instead
share a template and simply supply it under different names.

Again, your :ref:`theme.zcml <zcml>` would include ``z3c.template``
directives to do this::

  <configure  xmlns="http://namespaces.zope.org/zope"
              xmlns:i18n="http://namespaces.zope.org/i18n"
              xmlns:zcml="http://namespaces.zope.org/zcml"
              xmlns:z3c="http://namespaces.zope.org/z3c"
              xmlns:browser="http://namespaces.zope.org/browser"
              >
     <include package="z3c.template" file="meta.zcml" />


      <!--
      We don't have files on disk that match all the template names
      that Nikola likes to use by default. So lets set up some aliases
      to the files that we *do* have that implement the required
      functionality.
      -->
      <z3c:template
        template="index.tmpl.pt"
        name="archiveindex.tmpl"
        layer=".interfaces.IArchiveIndexPageKind"
        />

      <z3c:template
        template="generic_post_list.pt"
        name="tag.tmpl" />

      <z3c:template
        template="generic_post_list.pt"
        name="author.tmpl" />
    </configure>

.. _lookup-macros:

Macros
------

When you use the ``macro:``
`expression type <https://pypi.python.org/pypi/z3c.macro>`_
in a template, the
registered macro is *also* looked up based on the current context,
request, and view. Suppose we are in our ``disqus_page.pt`` rendering
with our ``IPost`` context, ``IPostPageKind`` request layer, and
``ICommentKindDisqus`` view.

::

    <div metal:use-macro="macro:comments" />

The registered macro named ``comments`` will be looked up for those
three objects.

Just as with templates, the macros that are found in :ref:`.macro.pt files
<auto-register-macros>` are registered for the most generic, least
specific interfaces possible. They can be augmented or replaced in
your :ref:`theme.zcml <zcml>` using the `z3c.macro
<https://pypi.python.org/pypi/z3c.macro>`_ directives::

    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:i18n="http://namespaces.zope.org/i18n"
               xmlns:zcml="http://namespaces.zope.org/zcml"
               xmlns:z3c="http://namespaces.zope.org/z3c"
               xmlns:browser="http://namespaces.zope.org/browser"
            >

      <include package="z3c.macro" />
      <include package="z3c.macro" file="meta.zcml" />

      <!-- Extra macros -->
      <z3c:macro
         name="comments"
         template="comment_helper.pt"
         for=".interfaces.IPost"
         view=".interfaces.ICommentKindDisqus"
         layer=".interfaces.IPostPageKind" />

    </configure>

By default, the name of the macro in the template file is the same as
the name it is registered with: the ``name`` attribute in the ZCML
element. If they need to be different, you can supply the ``macro``
attribute in ZCML.

For example, if we have two different kinds of comment systems in
``comment_helper.pt``::

     <tal:block>

        <metal:block metal:define-macro="comments-facebook">
           <!-- Stuff for Facebook comments -->
        </metal:block>
        <metal:block metal:define-macro="comments-disqus">
           <!-- Stuff for Disqus comments -->
        </metal:block>
     </tal:block>

We could register them and use them both for different comment
systems with this ZCML::

      <configure xmlns="http://namespaces.zope.org/zope"
                 xmlns:i18n="http://namespaces.zope.org/i18n"
                 xmlns:zcml="http://namespaces.zope.org/zcml"
                 xmlns:z3c="http://namespaces.zope.org/z3c"
                 xmlns:browser="http://namespaces.zope.org/browser"
              >

        <include package="z3c.macro" />
        <include package="z3c.macro" file="meta.zcml" />

        <!-- Extra macros -->
        <z3c:macro
           name="comments"
           macro="comments-disqus"
           template="comment_helper.pt"
           for=".interfaces.IPost"
           view=".interfaces.ICommentKindDisqus"
           layer=".interfaces.IPostPageKind" />
        <z3c:macro
           name="comments"
           macro="comments-facebook"
           template="comment_helper.pt"
           for=".interfaces.IPost"
           view=".interfaces.ICommentKindFacebook"
           layer=".interfaces.IPostPageKind" />

      </configure>


For more on using macros (and in particular, how to find a macro for a
*different* context), see :doc:`macros`.

Viewlets
--------

As you might have guessed, viewlets are handled the same way. When you
use the ``provider:`` `expression type
<https://pypi.python.org/pypi/zope.contentprovider#the-tales-provider-expression>`_
in a template, the resulting provider is found in the component
registry using the current context, request and view.

.. note:: Although the ``provider:`` expression type supports generic
          content providers, this package exclusively uses `viewlets
          <https://pypi.python.org/pypi/zope.viewlet>`_. This is
          because viewlets can be developed using only templates and
          ZCML, without any Python code.

Unlike macros and templates, there is no automatic registration for
viewlet managers and viewlets. Instead, they must all be registered in
ZCML.

Suppose we have a template that uses a viewlet::

  <head>
    ...
    <!--! The extensible viewlet manager; anyone can add things based
         on view, context and request/layer to it. -->
    <tal:block content="structure provider:extra_head" />
  </head>


We would set up and fill that viewlet with this ZCML::

    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:i18n="http://namespaces.zope.org/i18n"
               xmlns:zcml="http://namespaces.zope.org/zcml"
               xmlns:z3c="http://namespaces.zope.org/z3c"
               xmlns:browser="http://namespaces.zope.org/browser"
            >

      <include package="zope.viewlet" file="meta.zcml" />

      <!-- Extra head -->
      <!-- The normal extra head for a page is called 'default_extra_head' -->
      <browser:viewletManager
          name="extra_head"
          provides=".interfaces.IHtmlHeadViewletManager"
          class="zope.viewlet.manager.WeightOrderedViewletManager"
          permission="zope.Public"
          />

      <browser:viewlet
          name="default_extra_head"
          manager=".interfaces.IHtmlHeadViewletManager"
          template="v_index_extra_head.pt"
          permission="zope.Public"
          layer=".interfaces.IIndexPageKind"
          weight="0"
          />

      <browser:viewlet
          name="archive_index_extra_head"
          manager=".interfaces.IHtmlHeadViewletManager"
          template="v_archiveindex_extra_head.pt"
          permission="zope.Public"
          layer=".interfaces.IArchiveIndexPageKind"
          weight="1"
          />

      <!-- And so on as needed -->

    </configure>

For much more about viewlets, see :doc:`viewlets`.

.. _finding-views:

Views
-----

When you use the ``@@view_name`` syntax in a path expression, the
previous path element becomes the *context* and an adapter from just
context and request are looked up by that name.

Example template::

    <html metal:use-macro="context/@@base.tmpl/index/macros/base"
          xmlns:tal="http://xml.zope.org/namespaces/tal"
          xmlns:metal="http://xml.zope.org/namespaces/metal">

       ...
    </html>

The macro to use is looked for beginning with the expression
``context/@@base.tmpl``. This takes the context object of this
template and uses it to find the view (for the current request/layer)
named ``@@base.tmpl``. All the ``.tmpl.pt`` files are registered as
most generic, least specific named views :ref:`automatically
<auto-register-template-views>`. You can add your own view registrations
for specific combinations of context and request if desired, though
this usually requires writing Python code.

.. tip:: Any callable that accepts a context and request can be
         registered as a view. This package provides several other
         :doc:`helpful views <path_helpers>`.
