"""
cfgclasses are representations of a python tools CLI configuration options
built on `dataclasses <https://docs.python.org/3/library/dataclasses.html>`_. This
allows individual tools to focus on specifying their configuration structure
without the overhead of interacting with argparse and the typeless Namespace it
returns.

The primary entrypoint for this module is :class:`cfgclasses.ConfigClass` and
its ``parse_args()`` classmethod.

.. autoclass:: cfgclasses.ConfigClass
    :members:
.. autoclass:: cfgclasses.MutuallyExclusiveConfigClass
    :members:

Additionally the following functions are provided to simplify the creation of
the class fields.

.. autofunction:: cfgclasses.arg
.. autofunction:: cfgclasses.optional

At a lower level these functions instantiate these classes and add them to the
``dataclasses.field()`` metadata in the key ``cfgclasses.CFG_METADATA_FIELD``.

.. autodata:: cfgclasses.argspec.CFG_METADATA_FIELD

.. autoclass:: cfgclasses.ConfigOpts
.. autoclass:: cfgclasses.NonPositionalConfigOpts

There are also equivalents for the creation of nested
:class:`cfgclasses.ConfigClass` definitions.

.. autofunction:: cfgclasses.cfgtransform

Which in turn creates a :class:`cfgclasses.ConfigClassTransform` object in the
key ``cfgclasses.CFG_METADATA_FIELD``.

.. autoclass:: cfgclasses.ConfigClassTransform

There is an additional submodule :mod:`cfgclasses.transforms` containing several
common transform functions.

cfgclasses.transforms
---------------------

.. automodule:: cfgclasses.transforms

"""

from . import arghelper, argspec, configclass

__all__ = (
    *arghelper.__all__,
    *argspec.__all__,
    *configclass.__all__,
)

from .arghelper import *
from .argspec import *
from .configclass import *
