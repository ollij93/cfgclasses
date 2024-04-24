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
 2. A simpler specification via a decorator that a ``dataclass`` is itself a mutually exclusive group.

These two solutions are discussed in the following subsections.
However, if is the latter than has been selected for implementation.

1.1.1. Union type
-----------------
The following example shows how the ``Union`` type could be used to specify a mutually exclusive group of configuration items.

.. code-block:: python

    from dataclasses import dataclass

    @dataclass
    class DebugConfig:
        debug: bool

    @dataclass
    class QuietConfig:
        quiet: bool

    @dataclass
    class MyConfig:
        verbosity: Union[DebugConfig, QuietConfig]


This solution has the advantage that it is very flexible and even allows for groups of items to be mutually exclusive to one another (e.g. A and B can both be specified together but neither can be specified if C is).

Unfortunately there are a number of downfalls:
1. It is considered that the above is too verbose for the common case of a single mutually exclusive group.
2. ``argparse`` does not support the nesting of groups within mutually exclusive groups, so the feature of A and B being mutually exclusive to C cannot be supported.


1.1.2. ``dataclass`` as mutually exclusive group
-----------------------------------------------
This solution is much simpler and more in line with the common case of a single mutually exclusive group.

This is the solution that has been implemented.

The following example shows how the use of the ``mutually_exclusive`` decorator on the ``dataclass`` could be used to specify a mutually exclusive group of configuration items.

.. code-block:: python

    import cfgclasses
    from dataclasses import dataclass

    @cfgclasses.mutually_exclusive
    @dataclass
    class MyConfig:
        debug: bool
        quiet: bool


Here all the members of ``MyConfig`` are mutually exclusive to one another. The use of nesting is crucial to this solution to define which items are mutually exclusive to one another, and which are not.

A more complex example is shown below:

.. code-block:: python

    import cfgclasses
    from dataclasses import dataclass

    @cfgclasses.mutually_exclusive
    @dataclass
    class LoggingConfig:
        debug: bool
        quiet: bool

    @dataclass
    class MyConfig:
        name: str
        logging: LoggingConfig

In this case ``--debug`` and ``--quiet`` are mutually exclusive, but ``--name`` is not mutually exclusive to either of them.

2. Implementation
-----------------
A new ``@mutually_exclusive`` decorator is added that accepts a class and sets a marker attribute on that class.

This marker attribute is then checked for when adding argument groups to argparse, using ``add_mutually_exclusive_group()`` instead of ``add_argument_group()`` if the attribute is set.

Programmers then simply need to use the decorator on their ``dataclass`` to specify that it is a mutually exclusive group.
