# -*- coding: utf-8 -*-
"""
ZCML directives.

.. versionadded:: 0.0.1a2
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from zope import interface
from zope.interface.interface import InterfaceClass
#from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import PythonIdentifier
from zope.viewlet.interfaces import IViewletManager


from . import viewlets

class IViewletManagerDirective(interface.Interface):
    """
    Creates a new viewlet manager interface in the
    ``nti.nikola_chameleon.viewlets`` package.
    """

    id = PythonIdentifier(
        title=u"The class name of the interface",
        required=True
    )

    # TODO: Extend a viewlet manager interface?

def viewletManagerDirective(_context, id):
    id = str(id) # ensure native string
    if id in dir(viewlets): # pragma: no cover
        # The name functions as the identity, so this is
        # idempotent.
        return

    # We must do our work right now so that it can
    # be used by other directives.

    manager = InterfaceClass(
        id, (IViewletManager,),
        __doc__='Viewlet Manager',
        __module__='nti.nikola_chameleon.viewlets'
    )
    manager.setTaggedValue("zcml_created", True)

    setattr(viewlets, id, manager)


def _cleanUp():
    to_remove = []
    for name, value in vars(viewlets).items():
        try:
            if value.getTaggedValue('zcml_created'):
                to_remove.append(name)
        except (AttributeError, KeyError):
            pass

    for name in to_remove:
        delattr(viewlets, name)


try:
    from zope.testing import cleanup
except ImportError: # pragma: no cover
    pass
else:
    cleanup.addCleanUp(_cleanUp)
