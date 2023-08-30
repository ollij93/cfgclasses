"""
cfgclasses are representations of a python tools CLI configuration options
built on `dataclasses <https://docs.python.org/3/library/dataclasses.html>`_. This
allows individual tools to focus on specifying their configuration structure
without the overhead of interacting with argparse and the typeless Namespace it
returns.

The primary entrypoint for this module is :class:`cfgclasses.ConfigClass` and
its ``parse_args()`` classmethod.

.. autoclass:: cfgclasses.ConfigClass
.. autoclass:: cfgclasses.MutuallyExclusiveConfigClass

Additionally the following functions are provided to simplify the creation of
the class fields.

.. autofunction:: cfgclasses.arg
.. autofunction:: cfgclasses.optional
"""

from . import arghelper, configclass

__all__ = (
    *arghelper.__all__,
    *configclass.__all__,
)

from .arghelper import *
from .configclass import *
