=======================================
 Leveraging the Component Architecture
=======================================

Background
==========

If you're not familiar with component architectures, and
``zope.component`` in particular, please take a few minutes to read
:doc:`zca_background`.


Theory of Operation
===================

Three of the `the standard names
<https://docs.zope.org/zope2/zope2book/AppendixC.html#built-in-names>`_
available in templates play a particularly important part in the way
templates, macros and viewlets are used.

Those names are ``context``, ``request`` and ``view``. These names are
inherited from the Zope family of Web frameworks, but they have equal
relevance here.

The context is the object being rendered. It is most commonly a Nikola
post (represented by :class:`~nti.nikola_chameleon.interfaces.IPost`),
but it can also be a
:class:`~nti.nikola_chameleon.interfaces.IPostList` on index pages, or
:class:`~nti.nikola_chameleon.interfaces.IGallery`,
:class:`~nti.nikola_chameleon.interfaces.IListing`
or :class:`~nti.nikola_chameleon.interfaces.ISlide` on their
respective pages.

.. tip:: The `template variables
         <https://getnikola.com/template-variables.html>`_ for
         specific template pages are available from the ``context``
         object, in addition to being available from the ``options``
         dictionary. Using ``context`` can result templates that are
         more clear in their intent.

.. todo:: Rethink how we have these separated out. Maybe more should
          go on the view and less on the request?

The request (or layer) expresses the intent of the render. It tells us
the purpose of our rendering. It will always provide the
:class:`~nti.nikola_chameleon.interfaces.IPageKind` interface (it will
actually always provide one of the more specific interfaces that
better identifies what we're trying to render, such as
:class:`~nti.nikola_chameleon.interfaces.ITagsPageKind`).

.. todo:: Talk about component lookup: context, request/layer, view and how we
          can register macros and viewlets for each of those things.

.. todo:: Talk about what each represents (object in use, details about what
          we're asking for, how we're handling the asking).

.. todo:: Talk about layers applied to the "request".

.. todo:: Talk about the different page kinds.

.. todo:: Talk about comment systems.
