=========
 Changes
=========

0.0.1a2 (2017-10-14)
====================

- Map the Nikola ``messages`` function onto the native ``i18n``
  functionality of Chamleon. Attributes like ``i18n:translate`` are
  now preferred to explicit calls to ``options/messages`` when
  possible.

- Add support for viewlets. Several default viewlet managers are
  supplied, and a ZCML directive ``<browser:newViewletManager>`` is
  provided so themes can create new viewlet managers::

    <browser:newViewletManager id="ILeftColumn" />
    <browser:viewletManager
        name="left_column"
        provides=".viewlets.ILeftColumn" />

- Add a path adapter to easily get formatted dates from a post, either
  a static format (``post/formatted_date:webiso``) or dynamically from
  a variable (``post/formatted_date:?date_format``).

- Add a view to get the text of a post, respecting teaser settings:
  ``post/@@post_text/content``.

- Move feed support to a ``@@feeds`` view for headers, and a viewlet
  for body::

   <browser:viewlet
      name="feed_content_header"
      manager=".interfaces.IHtmlBodyContentHeaderViewletManager"
      class=".feeds.HTMLFeedLinkViewlet"
      layer=".interfaces.IAuthorPageKind"
      permission="zope.Public"
      weight="1"
      classification_name="author"
      />

- Add a view interface (``ICommentKind``) for comment systems. Only Disqus is
  currently supported. Note that this may move in the future to be a layer.

0.0.1a1 (2017-10-09)
====================

- Preliminary PyPI release. While this package is functional, it is
  not yet documented sufficiently to be of general use. It is also not
  expected to be fully stable.
