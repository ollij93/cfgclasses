Mutually Exclusive Groups
=========================

1. Problem Definition
---------------------

In argparse you can specify mutually exclusive groups of arguments. This allows the programmer to specify that the user may not configure one item if another item is also being configured.

A common case where this is used is when a program takes a ``--debug`` flag to output additional information, but also takes a ``--quiet`` flag to suppress any non-error output. These two flags are mutually exclusive, since it makes no sense to both output additional information and suppress non-error output.

``cfgclasses`` provides a way to specify this same relationship between configuration items.

1.1. Proposed solutions
-----------------------
There were two considered solutions to this problem:
 1. The use of the ``Union`` type to allow one of two subgroups to be specified.
 2. A simpler specification that a ConfigClass is itself a mutually exclusive group.

These two solutions are discussed in the following subsections.
However, if is the latter than has been selected for implementation.

1.1.1. Union type
-----------------
The following example shows how the ``Union`` type could be used to specify a mutually exclusive group of configuration items.

.. code-block:: python

    from cfgclasses import ConfigClass

    class DebugConfig(ConfigClass):
        debug: bool

    class QuietConfig(ConfigClass):
        quiet: bool

    class MyConfig(ConfigClass):
        verbosity: Union[DebugConfig, QuietConfig]


This solution has the advantage that it is very flexible and even allows for groups of items to be mutually exclusive to one another (e.g. A and B can both be specified together but neither can be specified if C is).

Unfortunately there are a number of downfalls:
1. It is considered that the above is too verbose for the common case of a single mutually exclusive group.
2. ``argparse`` does not support the nesting of groups within mutually exclusive groups, so the feature of A and B being mutually exclusive to C cannot be supported.


1.1.2. ConfigClass as mutually exclusive group
-----------------------------------------------
This solution is much simpler and more in line with the common case of a single mutually exclusive group.

This is the solution that has been implemented.

The following example shows how the ``ConfigClass`` type could be used to specify a mutually exclusive group of configuration items.

.. code-block:: python

    from cfgclasses import MutuallyExclusiveConfigClass
    from dataclasses import dataclass

    @dataclass
    class MyConfig(MutuallyExclusiveConfigClass):
        debug: bool
        quiet: bool


Here all the members of ``MyConfig`` are mutually exclusive to one another. The use of nesting is crucial to this solution to define which items are mutually exclusive to one another, and which are not.

A more complex example is shown below:

.. code-block:: python

    from cfgclasses import ConfigClass, MutuallyExclusiveConfigClass
    from dataclasses import dataclass

    @dataclass
    class LoggingConfig(MutuallyExclusiveConfigClass):
        debug: bool
        quiet: bool

    @dataclass
    class MyConfig(ConfigClass):
        name: str
        logging: LoggingConfig

In this case ``--debug`` and ``--quiet`` are mutually exclusive, but ``--name`` is not mutually exclusive to either of them.

2. Implementation
-----------------
A new ``add_argument_group()`` classmethod is added to ``ConfigClass``. This method takes in a ``argparse`` group and adds and returns a new group to it. This method is then invoked after building the ``Specification`` for a ``ConfigClass``, prior to adding its members to the parser group.

The default implementation of this new function is to call and return ``add_argument_group()`` on the given parser.

However, a new subclass of ``ConfigClass`` - ``MutuallyExclusiveConfigClass`` - overrides this method to instead invoke ``add_mutually_exclusive_group()`` on the given parser.

Programmers can then subclass ``MutuallyExclusiveConfigClass`` to define a mutually exclusive group of configuration items rather than subclassing ``ConfigClass``.
