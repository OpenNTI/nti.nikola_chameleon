===================
 Theme Inheritance
===================

nti.nikola_chameleon support themes that extend themes. In fact, with
a well designed and documented base theme, nti.nikola_chameleon makes
it easy to customize as much or as little as you'd like.

Extending a theme is just like :doc:`creating a theme <first_theme>`.
The only difference is that you need to specify the ``parent`` theme
that you're extending by name. For example, here's the theme meta file
for the ``bootstrap3-chamaleon`` theme, which extends the
``base-chameleon`` theme:

.. code-block:: ini
   :emphasize-lines: 9

   [Theme]
   engine = nti.nikola_chameleon
   author = NextThought
   author_url =
   license = Apache2
   based_on = Bootstrap 3 <https://getbootstrap.com/>
   tags = bootstrap
   parent = base-chameleon

   [Family]
   family = bootstrap3

   [Nikola]
   bootswatch = True

From that point on, you can override and customize the necessary
pieces of the theme. Specifically how you do that will depend on the
theme you're extending.

Replacing Files
===============

If you have a ``*.tmpl.pt`` with the same name as one from the parent
theme, your file will replace that file when it is used as :ref:`a
template name by Nikola <lookup-templates>` and when it is used as
:ref:`a view name <finding-views>` for the purposes of using macros.
(Make sure you define the necessary macros!) This is a little bit
blunt, so we don't usually recommend replacing entire files (or using
file views to find macro names for that matter).

Replacing Macros
================

Any macros you define with the same name (and specificity) as macros
defined by the parent theme will replace the parent theme macros. For
example, any macros defined in ``*.macro.pt`` files in your theme will
override such macros defined in ``*.macro.pt`` files in the parent
theme (because macros defined that way all have the same, very low,
specificity).

You can override a macro of a given name for only *some* kinds of
objects with an appropriate definition in your :ref:`theme.zcml
<lookup-macros>`.

Extending and Replacing Viewlets
================================

Adding to or replacing viewlets defined in the parent theme is the
same as doing so :ref:`in a single theme <multiple-viewlets>`: just
pay attention to the names and the specificity of your viewlet declarations.

ZCML Execution
==============

The ``theme.zcml`` files are executed from the base theme down to the
most derived theme. The execution context is the same for each
execution, so base themes can `provide features
<http://zopeconfiguration.readthedocs.io/en/latest/narr.html#making-specific-directives-conditional>`_
that child themes can test for.
