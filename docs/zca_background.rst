====================================================
 An Introduction to the Zope Component Architecture
====================================================

.. note:: This document is not intended to be a comprehensive guide to
          zope.component or component systems in general. It will only
          discuss concepts that are relevant to this package. For more
          information, see the `zope.component documentation
          <https://zopecomponent.readthedocs.io/en/latest/>`_ or `this
          guide <http://muthukadan.net/docs/zca.html>`_.

This document will provide a brief introduction to some of the
concepts in a component architecture and an example specifically of
using ``zope.component``. If you're already familiar with these
things, you can skip it.

Definitions
===========

For our purposes, we will define a *component* as a unit of software
that provides some specific functionality. What that functionality is
and what it does is the component's *interface*; a single component
may provide multiple different functions and thus multiple interfaces.
(Interfaces can also be thought of as a way to represent a particular
concept.)

A *component registry* provides us with a way to find components that
provide specific interfaces. Sometimes there can me multiple
components that can all provide the same interface (different ways to
implement a specific function), so we can choose between them based on
a *name*.

Sometimes a component will need particular other objects in order to
fulfill its function. In this case the component registry stores a
*factory*, and when we ask it for the component, we provide the
objects we want to work with to the registry. The registry then finds
the correct factory, passes it the objects, and returns the resulting
component. This process is called using an *adapter* because the
factory *adapts* the objects we give it to produce the desired
component. (In Python, factories are often classes, and the returned
component is just an instance of the class.)

Certain types of factories will know how to adapt certain kinds of
objects, while other types of factories will know how to adapt others,
so the component registry will inspect the objects we give it to find
the most specific factory---the one that's the best fit for the
objects we give.

In Python, objects are components. Interfaces can either be
represented by classes, or more flexibly by the interface objects
created by ``zope.interface``. (These are more flexible than classes
because they can be added and removed from particular objects
independently of any code.)

Example
=======

For example, let's imagine we're working in the United Nations general
assembly, and we need to provide language translators for the various
diplomats.

We'll begin by defining an interface for someone who can speak a
language, plus some specific language examples:

.. doctest::

   >>> from zope.interface import Interface
   >>> class ILanguageSpeaker(Interface):
   ...    """Someone who can speak a language"""
   >>> class IGermanSpeaker(ILanguageSpeaker):
   ...    """Someone who can speak German."""
   >>> class ISpanishSpeaker(ILanguageSpeaker):
   ...    """Someone who can speak Spanish"""
   >>> class IFrenchSpeaker(ILanguageSpeaker):
   ...    """Someone who can speak French."""


Now we'll create some diplomat classes and let them speak their native
language (because the class is a factory, this is called
*implementing* an interface; the resulting class instance is said to
*provide* the interface):

.. doctest::

    >>> from zope.interface import implementer

    >>> class SensibleRepr(object):
    ...     def __repr__(self):
    ...        return '<%s>' % (type(self).__name__)

    >>> @implementer(IGermanSpeaker)
    ... class GermanDiplomat(SensibleRepr):
    ...    """The German diplomat speaks German."""

    >>> @implementer(ISpanishSpeaker)
    ... class SpanishDiplomat(SensibleRepr):
    ...    """The Spanish diplomat speaks Spanish."""

    >>> @implementer(IFrenchSpeaker)
    ... class FrenchDiplomat(SensibleRepr):
    ...    """The French diplomat speaks French."""

    >>> french_diplomat = FrenchDiplomat()
    >>> spanish_diplomat = SpanishDiplomat()
    >>> german_diplomat = GermanDiplomat()

None of the diplomats speak the same language and are thus unable to
communicate. Let's remedy that by providing a translator. We'll first
define an interface to represent someone that can translate:

.. doctest::

    >>> class ILanguageTranslator(ILanguageSpeaker):
    ...    """Someone who can translate between languages. """

If we ask the component registry for a translator for the Spanish and German
diplomats, we won't find anyone yet (we use
:func:`zope.component.getMultiAdapter` to request an adapter for
multiple objects):

.. doctest::

    >>> from zope import component
    >>> component.getMultiAdapter((spanish_diplomat, german_diplomat), ILanguageTranslator)
    Traceback (most recent call last):
    ...
    zope.interface.interfaces.ComponentLookupError: ((<SpanishDiplomat...>, <GermanDiplomat...>),...


Let's create someone who can speak both languages:

.. doctest::

    >>> @implementer(ISpanishSpeaker, IGermanSpeaker)
    ... class Steve(object):
    ...    """Steve speaks two languages."""
    ...
    ...    def __repr__(self):
    ...       return "<Hi, I'm Steve>"
    >>> steve = Steve()

Now lets hire that person and put them to work as a translator by
registering them in the component registry (notice that the object
that implements ``ILanguageTranslator`` is given the two people who
need the translating done, but Steve doesn't need them to do his
job---he can translate for any Spanish and German speakers---so we
just use a lambda function):

.. doctest::

    >>> component.provideAdapter(lambda spanish_speaker, german_speaker: steve,
    ...                          provides=ILanguageTranslator,
    ...                          adapts=(ISpanishSpeaker, IGermanSpeaker))

We can now find someone who will translate for the diplomats:

.. doctest::

    >>> component.getMultiAdapter((spanish_diplomat, german_diplomat), ILanguageTranslator)
    <Hi, I'm Steve>

Extending Interfaces
--------------------

But what if the diplomats need to have a conversation about Security
Council matters, something that Steve isn't cleared for? We'll need an
interface to represent a translator with a security clearance:

.. doctest::

   >>> class ISecureLanguageTranslator(ILanguageTranslator):
   ...   """A secure translator."""

We'll imagine that computer translation skills are proceeding apace
and are good enough for this sort of thing, so we'll create a computer
that can speak all the languages. As a computer, it's considered
inherently secure:

.. doctest::

   >>> @implementer(ISecureLanguageTranslator,
   ...              ISpanishSpeaker,
   ...              IGermanSpeaker,
   ...              IFrenchSpeaker)
   ... class ComputerTranslator(object):
   ...    def __init__(self, *args):
   ...        self.a, self.b = args
   ...    def __repr__(self):
   ...        return '<ComputerTranslator for %r %r>' %(self.a, self.b)

(The computer might want to know exactly who it is translating
for---maybe to adapt to regional dialects---so we'll let it have
access to the diplomats.) Now we can install the computer to do some
secure translating:

.. doctest::

    >>> component.provideAdapter(ComputerTranslator,
    ...                          provides=ISecureLanguageTranslator,
    ...                          adapts=(ISpanishSpeaker, IGermanSpeaker))
    >>> component.provideAdapter(ComputerTranslator,
    ...                          provides=ISecureLanguageTranslator,
    ...                          adapts=(ISpanishSpeaker, IFrenchSpeaker))

The diplomats can now have a secure conversation:

.. doctest::

    >>> component.getMultiAdapter((spanish_diplomat, german_diplomat), ISecureLanguageTranslator)
    <ComputerTranslator for <SpanishDiplomat> <GermanDiplomat>>

Steve only speaks Spanish and German, but what if the Spanish and
French speakers want to have a (non-secure) conversation about their home town
football teams? Steve can't do it. Can anyone?

.. doctest::

    >>> component.getMultiAdapter((spanish_diplomat, french_diplomat), ILanguageTranslator)
    <ComputerTranslator for <SpanishDiplomat> <FrenchDiplomat>>

The computer can! Because ``ISecureLanguageTranslator`` extends
``ILanguageTranslator``, when we ask for the latter, the registry is
smart enough to know that a secure translator can just as well handle
non-secure communications.

Names
-----

Steve is a great German speaker, but his Spanish accent is a bit
rough, and the Spanish diplomat would prefer someone a bit easier to
understand, so we'll hire someone else.

.. doctest::

    >>> @implementer(ISpanishSpeaker, IGermanSpeaker)
    ... class Joe(object):
    ...    """Joe speaks two languages."""
    ...
    ...    def __repr__(self):
    ...       return "<Hi, I'm Joe>"
    >>> joe = Joe()

This time, we'll register the translator so that the Spanish diplomat
can ask for the translator by name:

.. doctest::

    >>> component.provideAdapter(lambda spanish_speaker, german_speaker: joe,
    ...                          name="Joe",
    ...                          provides=ILanguageTranslator,
    ...                          adapts=(ISpanishSpeaker, IGermanSpeaker))

    >>> component.getMultiAdapter((spanish_diplomat, german_diplomat),
    ...                           ILanguageTranslator,
    ...                           name="Joe")
    <Hi, I'm Joe>

Steve is still available by default:

.. doctest::

    >>> component.getMultiAdapter((spanish_diplomat, german_diplomat), ILanguageTranslator)
    <Hi, I'm Steve>
