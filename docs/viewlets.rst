================
 Using Viewlets
================

.. currentmodule:: nti.nikola_chameleon.interfaces
.. highlight:: xml

`Viewlets <https://pypi.python.org/pypi/zope.viewlet>`_ are a
mechanism for creating pluggable themes.

They are broadly similar to :doc:`macros <macros>`, in that they allow
the contents of a particular part of a template to be defined
elsewhere. Moreover, they are also registered based on the context,
request and view, allowing specific viewlets to be used for specific
types of objects. There are some important differences, though:

- Multiple viewlets can create content for one spot. (If a only a
  single viewlet is defined, it's functionally very much like a macro
  with no slots.)
- They must be registered in :ref:`ZCML <zcml>`. There is currently no support for
  automatically registering viewlets from the filesystem.
- They have a hierarchy in naming: a template references a *viewlet
  manager*, and the viewlets are attached to the viewlet manager.

They have an extra level of flexibility because they can be written
partly or entirely in Python. However, this document will only focus
on how they can be used with template files.

Viewlet Managers and the ``provider:`` Expression
=================================================

We'll jump right in with an example from the ``base-chameleon`` theme.
First, here is a (simplified) template called
``generic_post_list.pt``:

.. code-block:: xml
   :emphasize-lines: 5

    <html xmlns:tal="http://xml.zope.org/namespaces/tal"
          xmlns:metal="http://xml.zope.org/namespaces/metal">
       ...
       <body>
        <article tal:replace="structure provider:post_list_article" />
       </body>
    </html>

The ``provider:`` expression is new here. That will look up and invoke
a `content provider
<https://pypi.python.org/pypi/zope.contentprovider>`_.

Viewlet Managers
----------------

In the context of nti.nikola_chameleon, that's almost always going to
be a viewlet manager. A viewlet manager is responsible for finding all
the applicable viewlets attached to it, finding out which ones are
available at the given time, sorting them, and then rendering them.
This package provides one default viewlet manager,
:class:`nti.nikola_chameleon.view.ConditionalViewletManager` that does
all of those steps. It sorts viewlets based on their ``weight``
attribute, and will disable viewlets that have their ``available``
attribute (if one exists) set to a false value.


So that's the first step in using viewlets (after deciding where in
the template viewlets might be useful, of course): define your viewlet
manager. This is done in ZCML:

.. code-block:: xml
   :emphasize-lines: 10,11

   <configure xmlns="http://namespaces.zope.org/zope"
             xmlns:i18n="http://namespaces.zope.org/i18n"
             xmlns:zcml="http://namespaces.zope.org/zcml"
             xmlns:z3c="http://namespaces.zope.org/z3c"
             xmlns:browser="http://namespaces.zope.org/browser" >

    <include package="zope.viewlet" file="meta.zcml" />
    <include package="nti.nikola_chameleon" file="meta.zcml" />

    <browser:newViewletManager id="IPostListArticle" />
    <browser:viewletManager
        name="post_list_article"
        provides=".viewlets.IPostListArticle"
        class=".view.ConditionalViewletManager"
        permission="zope.Public"
        />
    </configure>

The line ``<browser:newViewletManager id="IPostListArticle" />``
creates a new kind of viewlet manager. This is important because, as
you'll see, individual viewlets are attached to the *kind* of the
viewlet manager (not its name). In advanced cases, this allows for a
hierarchy of viewlet managers to be defined, but in most cases each
individual viewlet manager should use its own type.

.. note:: There are a handful of pre-defined kinds of viewlet managers
          in :mod:`nti.nikola_chameleon.interfaces`:
          :class:`IHtmlHeadViewletManager`,
          :class:`IHtmlBodyContentViewletManager`, :class:`IHtmlBodyContentHeaderViewletManager`,
          :class:`IHtmlBodyContentFooterViewletManager` and
          :class:`IHtmlBodyFooterViewletManager`. These are very
          generic and in complex situations it would be easy to
          accidentally register too much on any given kind of viewlet
          manager, so only use them with caution. They can work well
          for simple themes or when well documented, though.

The next line, beginning with ``<browser:viewletManager`` actually
creates and registers a viewlet manager. We give it a name
(``post_list_article``) by which a ``provider:`` expression can find
it, we set it up to be the kind of viewlet manager we just defined
(``provides=".viewlets.IPostListArticle"``), and we tell it what sort
of class will implement the viewlet functionality.

.. note:: Using ``class=".view.ConditionalViewletManager"`` is always
          recommended.

.. note:: Setting ``permission="zope.Public"`` is unfortunately
          required at this time. In the future, a directive might be
          created that doesn't require this.

.. note:: The ``viewletManager`` directive does allow the ``for``,
          ``layer`` and ``view`` attributes to register the viewlet
          manager for a particular context, request and view,
          respectively. Usually registering individual *viewlets* for
          particular contexts, requests and views themselves is enough
          and we can leave these attributes out. However, in advanced
          cases, where you want to use a completely different kind of
          viewlet manager (``IPostListArticle`` in this case) of the
          same name (``post_list_article``) this may be helpful. It
          can also be helpful to disable an entire viewlet manager
          when extending a theme.

Viewlet Manager Templates
-------------------------

Not seen here is the ``template`` argument. This allows you to provide
a template into which the viewlets attached to the manager will be
rendered. The template is passed the attached viewlets in its
``viewlets`` option. If you do not specify a template, viewlets
default to being rendered one after the other, something like this::

    <tal:block xmlns:tal="http://xml.zope.org/namespaces/tal"
               tal:repeat="viewlet options/viewlets">
        <tal:block tal:replace="structure viewlet" />
    </tal:block>

Viewlets
========

Now that we have a viewlet manager, we can add individual viewlets to
it. For our purposes, a viewlet is a template that gets run to fill in
a piece of content for its viewlet manager. Recall that viewlets are
associated with viewlet manager via the viewlet manager's kind, or interface.
Again, this is done in ZCML:

.. code-block:: xml
   :emphasize-lines: 11,12,13,20,21,22

   <configure xmlns="http://namespaces.zope.org/zope"
             xmlns:i18n="http://namespaces.zope.org/i18n"
             xmlns:zcml="http://namespaces.zope.org/zcml"
             xmlns:z3c="http://namespaces.zope.org/z3c"
             xmlns:browser="http://namespaces.zope.org/browser" >

    <include package="zope.viewlet" file="meta.zcml" />

    <browser:viewlet
        name="default_article"
        manager=".viewlets.IPostListArticle"
        template="v_generic_article_post_list.pt"
        layer=".interfaces.ITagPageKind"
        permission="zope.Public"
        article_class="tagpage"
        />

    <browser:viewlet
        name="default_article"
        manager=".viewlets.IPostListArticle"
        template="v_generic_article_post_list.pt"
        layer=".interfaces.IAuthorPageKind"
        permission="zope.Public"
        article_class="authorpage"
        />
   </configure>

Here we have defined two viewlets and attached them to the
``IPostListArticle`` viewlet manager with their ``manager`` attribute.
Each of them has specified a ``template`` to run and a name (as well
as the boilerplate ``permission`` attribute). They have been specified
for different request layers with the ``layer`` attribute. Because the
layers are orthogonal (a request provides only one page kind), at most
only one of these two viewlets will be found for any given request.
(We could also specify ``view`` and ``context`` attributes to further
narrow it down, if necessary.)

Passing Parameters
------------------

Notice that they both use the same ``template`` argument. And what's
that ``article_class`` attribute for? Let's take a look at that
template file, ``v_generic_article_post_list.pt``:

.. code-block:: xml
   :emphasize-lines: 1

    <article class="${view/article_class}"
           xmlns:tal="http://xml.zope.org/namespaces/tal"
	       xmlns:metal="http://xml.zope.org/namespaces/metal">
      <header>
          <tal:block replace="structure provider:content_header" />
      </header>

      <ul metal:use-macro="macro:html_posts_postlist">
          <li>A post</li>
      </ul>
    </article>

It turns out that all the extra attributes you specify in ZCML get
turned into attributes on the ``view`` object when the viewlet runs.
So we are able to "parameterize" the template in this way. It turns
out the only thing we want to do differently when we are listing
posts for a tag and posts for an author is use a different CSS class
name (``class="${view/article_class}"``).

There is a subtlety here: The ``view`` object while the viewlet
template renders is *not* the same as the ``view`` object when the
template was called.

.. caution:: Because :class:`ICommentKind` is currently based on the
             view, access to the type of comment system in use is lost
             when rendering a viewlet.

.. _multiple-viewlets:

Overwriting, Extending, and Multiple Viewlets
=============================================

We've seen an example where only one viewlet at a time is expected to
match. What if we may actually want more than one viewlet to render?
For example, we may have some standard styles that we always want to
put into the HTML ``<head>`` (while allowing themes that extend us to
modify or replace those), while also allowing for additional styles to
be added when rendering particular types of pages (again,
context/request/view discriminators).

This is where the ``name`` attribute becomes useful.

- A more specific registration with the same ``name`` will *replace*
  the less specific registration.
- Registrations with a different ``name`` will *extend* the set of
  applicable viewlets.
- Equally specific registrations with the same ``name`` aren't
  allowed, but an extending theme can replace them.

Let's look at an example. Suppose our main template defines the
``<head>`` to use a content provider::

    <html>
      <head>
         ...
        <!--! The extensible viewlet manager; anyone can add things based
             on view, context and request/layer to it. -->
        <tal:block content="structure provider:extra_head" />
      </head>
    </html>


We can then define this viewlet manager and add some specific viewlets
to it in ZCML::

  <configure>
    ...
    <!-- Extra head -->
    <!-- The normal extra head for a page is called 'default_extra_head' -->
    <browser:viewletManager
      name="extra_head"
      provides=".interfaces.IHtmlHeadViewletManager"
      class="zope.viewlet.manager.WeightOrderedViewletManager"
      permission="zope.Public"
      />

    <!-- posts, pages, stories and books all have the same extra header -->
    <browser:viewlet
      name="default_extra_head"
      manager=".interfaces.IHtmlHeadViewletManager"
      template="v_post_extra_head.pt"
      permission="zope.Public"
      layer=".interfaces.IPostPageKind"
      weight="0"
      />
    <!-- books get extra -->
    <browser:viewlet
      name="book_extra_head"
      manager=".interfaces.IHtmlHeadViewletManager"
      template="v_book_extra_head.pt"
      permission="zope.Public"
      layer=".interfaces.IBookPageKind"
      weight="1"
      />
     ...
  </configure>

We register a viewlet called ``default_extra_head`` for each page
kind. (For posts, pages and stories we rely on the fact that all the
specific page kinds extend the generic :class:`IPostPageKind`
interface to only write that down once.) We then use a new name to
define the extra style that books get when we render
``IBookPageKind``; if we had used the same name again, we would have
hidden the default head.

This is also an example of sorting viewlets: we specify the ``weight``
attribute to be able to ensure what order the styles are added in.

.. _supplied-viewlets:

Supplied Viewlets
=================

This package supplies one viewlet for producing links to feeds in HTML
bodies. See the documentation for
:class:`nti.nikola_chameleon.feeds.HTMLFeedLinkViewlet` for more
information.
