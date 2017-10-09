# -*- coding: utf-8 -*-
"""
Interfaces for rendering Nikola with chameleon.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nikola.post import Post
from zope import interface

class ITemplate(interface.Interface):
    """
    A template.
    """

    def __call__(view, **kwargs):
        "Called to render."


class IPost(interface.Interface):
    """
    A post.
    """

interface.classImplements(Post, IPost)

class IPageKind(interface.Interface):
    """
    The type of page being rendered.

    Specific types of pages will have a more specific
    interface.

    This is similar to IBrowserLayer concept in Zope 3.
    """

    interface.taggedValue('__pagekinds__', ())

class IListPageKind(IPageKind):
    "A page that is a list"
    # 'list' in pagekind
    interface.taggedValue('__pagekinds__', (u'list',))

class IAuthorsPageKind(IListPageKind):
    "The page for listing authors"

    # 'list' and 'authors_page' in pagekind
    interface.taggedValue('__pagekinds__', (u'list', u'authors_page'))

class IAuthorPageKind(IListPageKind):
    "The page for listing an author"

    # 'list' and 'author_page' in pagkeind
    interface.taggedValue('__pagekinds__', (u'list', u'author_page'))

class ITagsPageKind(IListPageKind):
    "The page for listing tags"

    # 'list' and 'tags_page' in pagekind
    interface.taggedValue('__pagekinds__', (u'list', u'tags_page'))

class ITagPageKind(IListPageKind):
    """The page for listing a tag"""

    # 'list' and 'tag_page' in pagkeind
    interface.taggedValue('__pagekinds__', (u'list', u'tag_page'))

class IGalleryPageKind(IPageKind):
    """A gallery page"""

    # 'gallery_page' in pagkeind
    interface.taggedValue('__pagekinds__', (u'gallery_page',))

class IListingPageKind(IPageKind):
    """A listing page"""

    # 'listing' in pagkeind
    interface.taggedValue('__pagekinds__', (u'listing',))

class IArchivePageKind(IListPageKind):
    """An archive page"""

    # 'list' and 'archive_page' in pagekind
    interface.taggedValue('__pagekinds__', (u'list', u'archive_page'))

class IIndexPageKind(IPageKind):
    """An index page"""

    # 'index' in pagkekind
    interface.taggedValue('__pagekinds__', (u'index',))

class IMainIndexPageKind(IIndexPageKind):
    """The main index"""

    # 'index' and 'main_index' in pagkeind
    interface.taggedValue('__pagekinds__', (u'index', u'main_index'))

class IPostPageKind(IPageKind):
    """A blog post"""

    # 'post_page' in pagekind
    interface.taggedValue('__pagekinds__', (u'post_page',))

class IPagePageKind(IPageKind):
    """A page"""

    # 'page_page' in pagekind
    interface.taggedValue('__pagekinds__', (u'page_page',))

class IStoryPageKind(IPagePageKind):
    """A story page"""

    # 'story_page' and 'page_page' in pagekind
    interface.taggedValue('__pagekinds__', (u'page_page', 'story_page',))

class IPostPage(IPost, IPageKind):
    """
    A page being rendered by a post.
    """

    interface.taggedValue('__pagekinds__', ())

def _build(iface, result):
    kinds = iface.getTaggedValue('__pagekinds__')
    kinds = frozenset(kinds)
    if kinds in result and kinds: # pragma: no cover
        raise ValueError("Duplicate pagkeinds", kinds, iface)

    if kinds not in result:
        result[kinds] = iface

    for sub in iface.dependents.keys():
        _build(sub, result)

    return result

PAGEKINDS = _build(IPageKind, {})
