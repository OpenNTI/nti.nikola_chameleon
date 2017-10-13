==================
 Creating a Theme
==================

.. highlight:: html

Creating a theme proceeds as `documented in the Nikola reference
<https://getnikola.com/theming.html#>`_. This document will focus on
the template features that nti.nikola_chameleon provides. Make sure
you've read :doc:`getting_started` before reading this.

Your theme should be laid out according to the Nikola documentation.
You'll need to specify ``nti.nikola_chameleon`` as the ``engine`` in
your theme meta file.

The only directory that nti.nikola_chameleon is interested in is your
``templates/`` folder.

There are three types of files that nti.nikola_chameleon will look for
in this directory: templates, macros (helpers) and ZCML configuration.
A complete them can be written just with template files and (optionally,
but helpfully) macro files.

.. note:: This document will contain frequent mentions of the ways the
          component architecture can be used to make themes
          flexible and make changing and customizing them through
          inheritance or configuration easier. You are not required to
          use these features if you don't want to. You can build an
          entire theme just based on the files in the templates
          directory and the Chameleon ``load:`` expression.

.. _auto-register-templates:

Templates
=========

Files in the templates directory that match the pattern ``*.tmpl.pt``
are ZPT files that Nikola can directly use as templates (when stripped
of the ``.pt`` suffix). For example, ``index.tmpl.pt`` will be used
when Nikola requests ``index.tmpl``. Nikola maintains `a list
<https://getnikola.com/theming.html#templates>`_ of the various
templates it may use by default (although a number of those templates,
such as ``base.tmpl`` and ``archive_navigation_helper.tmpl`` are
internal helpers specific to the default Nikola theme implementations,
even if they are not called out as such).

The most obvious way to create a theme, then, is to create a
``.tmpl.pt`` file for each standard template that Nikola uses and
populate it with your design.

.. _auto-register-template-views:

Views for Sharing Macros
------------------------

Each ``.tmpl.pt`` file found in this directory is registered as a
default view with the same name so it can be found via traversal. This
is useful to be able to share macros and fill slots. For example, if
``base.tmpl.pt`` is the generic "layout" template and it defines the
macro ``base`` with the slot ``content``, the ``story.tmpl.pt`` may
take advantage of that layout by using that macro and filling in that
slot, finding the ``base.tmpl`` macro via traversal::

    <html metal:use-macro="context/@@base.tmpl/index/macros/base"
          xmlns:i18n="http://xml.zope.org/namespaces/i18"
          xmlns:metal="http://xml.zope.org/namespaces/metal">

        <article metal:fill-slot="content">
             My content template goes here
         </article>
    </html>

Although the standard Chameleon `load:
<https://chameleon.readthedocs.io/en/latest/reference.html#load>`_
expression type is available, the traversal based mechanism is much
more flexible because it allows themes that extend yours to provide a
new ``base.tmpl`` view. It is also useful to provide different macros
depending on the ``context`` object (or whatever objects you traverse
through). For more on that, see :doc:`using_zca`, :doc:`inheritance`
and :ref:`zcml`.

.. _auto-register-macros:

Macros
======

Files in the templates directory that match the pattern ``*.macro.pt``
are not used directly by Nikola as templates. Instead, they are parsed
to find all of the macros they define. Each macro is registered as the
default macro for its name so that the ``macro:`` expression type from
`z3c.macro <https://pypi.python.org/pypi/z3c.macro>`_ can be used to
find it.

The most direct translation from the Nikola base template
implementations and documentations would be to have each
``_helper.tmpl`` become a ``.macro.pt`` file, for example,
``math_helper.macro.pt`` and ``post_helper.macro.pt`` for
``math_helper.tmpl`` and ``post_helper.tmpl``, respectively.

Continuing our story example above, suppose the file
``post_helper.macro.pt`` defined an ``html_title`` macro::

  <metal:block xmlns:tal="http://xml.zope.org/namespaces/tal"
               xmlns:metal="http://xml.zope.org/namespaces/metal"
               xmlns:i18n="http://xml.zope.org/namespaces/i18n">

    <metal:block metal:define-macro="html_title">
      <h1 class="p-name entry-title" itemprop="headline name"
          tal:define="title options/title"
          tal:condition="python:title and not context.meta('hidetitle')">
        <a href="${context/permalink}" class="u-url">${context/title}</a>
      </h1>
    </metal:block>

  </metal:block>

Our ``story.tmpl.pt`` (and other files) could use this macro like so::

    <html metal:use-macro="context/@@base.tmpl/index/macros/base"
          xmlns:i18n="http://xml.zope.org/namespaces/i18"
          xmlns:metal="http://xml.zope.org/namespaces/metal">

        <article metal:fill-slot="content">
            <header>
               <h1 metal:use-macro="macro:html_title">Replaced by the title</h1>
            </header>
            My content template goes here
         </article>
    </html>

Now, we could have implemented that with the ``load:`` expression
type::

    <html metal:use-macro="context/@@base.tmpl/index/macros/base"
          xmlns:i18n="http://xml.zope.org/namespaces/i18"
          xmlns:metal="http://xml.zope.org/namespaces/metal">

        <article metal:fill-slot="content">
            <header tal:define="post_helper load:post_helper.macro.pt">
               <h1 metal:use-macro="post_helper/macros/html_title">Replaced by the title</h1>
            </header>
            My content template goes here
         </article>
    </html>


However, as with templates, the use of the ``macro:`` expression type
allows themes to extend us and replace that macro with their own
version, and it allows us to produce macros that do different things
depending on context. For more on that, see :doc:`using_zca`,
:doc:`inheritance` and :ref:`zcml`.

.. caution:: If you implement a macro of the same name in two
             different files, nti.nikola_chameleon will warn you, and
             the one in the last file that defines it will be what is
             registered.

.. seealso:: :doc:`macros`

.. _zcml:

ZCML
====

Finally, after registering all the templates and macros, if your
directory contains a ``theme.zcml`` file, nti.nikola_chameleon will
load that file. It is a standard `zope.configuration
<http://zopeconfiguration.readthedocs.io/en/latest/>`_ file.

You can use this file to replace any registrations that
nti.nikola_chameleon makes by default. You can also use it to provide
more specific versions of macros, tailored to particular types of
objects, and you can use it to provide viewlets. (For more on viewlets
see :doc:`viewlets`.) You can also use it to rename entire templates or
register more specific templates.

The ``theme.zcml`` file is executed in the nti.nikola_chameleon
package. This means that you can easily refer to the various object
types with a simple . prefix.

If your theme extends another theme, the ZCML will be executed in
order of theme inheritance; this allows themes to replace
registrations from earlier themes. For more on theme inheritance, see
:doc:`inheritance`.

.. TODO: WRITE THE DOCUMENTS REFERENCED ABOVE.

Let's take a look at an example. Don't worry if much of it doesn't
make sense yet, we'll cover those concepts later.

::

    <!-- -*- mode: nxml -*- -->
    <configure	xmlns="http://namespaces.zope.org/zope"
            xmlns:i18n="http://namespaces.zope.org/i18n"
            xmlns:zcml="http://namespaces.zope.org/zcml"
            xmlns:z3c="http://namespaces.zope.org/z3c"
            xmlns:browser="http://namespaces.zope.org/browser"
            >

      <include package="z3c.macro" />
      <include package="z3c.macro" file="meta.zcml" />
      <include package="z3c.template" file="meta.zcml" />
      <include package="zope.viewlet" file="meta.zcml" />
      <include package="nti.nikola_chameleon" file="meta.zcml" />

      <!-- Extra macros -->
      <z3c:macro name="open_graph_metadata"
             for=".interfaces.IPost"
             view="*"
             template="post_helper.pt"
             layer="*" />

      <!-- Viewlets and Viewlet managers -->
      <!-- To extend, use a new name. To replace use the same name
           with at least as specific a registration.
      -->

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

Other Files
===========

Any other files in this directory are ignored by nti.nikola_chameleon.
You can use plain ``.pt`` files to implement additional macros or
entire templates. You can refer to them in your ``theme.zcml`` file
(preferred) and access them via ``macro:`` expressions or traversal,
or you could explicitly reference them using ``load:`` expressions.
