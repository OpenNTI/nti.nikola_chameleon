==============
 Path Helpers
==============

.. highlight:: xml

nti.nikola_chameleon provides some helpers for use in path
expressions. These are implemented either as *path adapters*, which
use a ``namespace:name`` syntax, or as :ref:`views <finding-views>`,
which use ``@@view_name`` syntax. Both of these methods :doc:`leverage
the component architecture <using_zca>`.

This document will mention each path helper provided, and where
appropriate, direct you to more information.

Post Helpers
============

These helpers are applied to any
:class:`~nti.nikola_chameleon.interfaces.IPost` object.

Formatted Date
--------------

The post object has a ``formatted_date`` method that produces a string
representing a date, and which requires one parameter, the name of the
date format. There is a standard format called ``webiso``, and the
user-configured date format is at ``options/date_format``.

The :class:`formatted_date
<nti.nikola_chameleon.adapters.FormattedDatePathAdapter>` path adapter
lets us call this function easily in a path expression.

.. list-table::
   :header-rows: 1

   * - Type
     - Python Expression
     - Path Expression
   * - Constant
     - ``python:post.formatted_date('webiso')``
     - ``post/formatted_date:webiso``
   * - Variable
     - ``python:post.formatted_date(options['date_format'])``
     - ``post/formatted_date:?date_format``

Meta
----

Posts have a method called ``meta`` that returns metadata. It takes a
string argument naming what metadata to return. Although these are
almost always used in templates in a static way, it is possible that
the metadata might be a variable.

The :class:`meta
<nti.nikola_chameleon.adapters.MetaPathAdapter>` path adapter
lets us call this function easily in a path expression.

.. list-table::
   :header-rows: 1

   * - Type
     - Python Expression
     - Path Expression
   * - Constant
     - ``python:post.meta('type')``
     - ``post/meta:type``
   * - Variable
     - ``python:post.meta(options['meta'])``
     - ``post/meta:?meta``

Post Text
---------

The ``text`` method on a post can take an optional parameter telling
it to truncate to a teaser length. This is configurable by the user
for index pages.
The :class:`post_text <nti.nikola_chameleon.view.PostTextView>` view
provides helpers to automatically take this into account.

Typical example::

      <tal:block tal:repeat="post context/posts">
        <article tal:define="post_text post/@@post_text"
                 class="h-entry post-${post/meta:type}
                        ${post_text/preview}">
            <div class="p-${post_text/content_kind}
                        entry-${post_text/content_kind}"
                 tal:content="structure:post_text/content">
                The content of the post.

                This may be just a teaser.
            </div>
        </article>
      </tal:block>

Generic Views
=============

These view objects are registered as default views for any object. You
can override that registration for something more specific if needed.

.. seealso:: :ref:`supplied-viewlets`

Feeds
-----

The :class:`feeds <nti.nikola_chameleon.feeds.Feeds>` view provides
helpers for producing RSS and Atom links in the header of pages. See
the methods defined there for more information.

Typical usage::

    <tal:block xmlns:tal="http://xml.zope.org/namespaces/tal"
               tal:define="kind options/kind|nothing;
                           feeds context/@@feeds">
      ${structure:python:feeds.feed_translations_head(kind=kind , feeds=False)}
    </tal:block>

.. _macros-view:

Macros
------

.. seealso:: :doc:`macros`


The :class:`macros <nti.nikola_chameleon.macro.NamedMacroView>`
view provides an alternative to the ``macro:`` expression type. It is used
when you wish to look up a macro having a different *context* than the
current context. The object you traverse through to reach the
``@@macros`` view becomes the context used to find and execute the
macro. This is most helpful when dealing with a list of posts.

Typical usage::

    <div tal:repeat="post context/posts">
      ...
      <p metal:use-macro="post/@@macros/comment_link"
         class="commentline" />
    </div>
