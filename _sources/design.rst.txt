Design
======

This page provides design details for the ``cfgclasses`` module.

1. Problem Definition
---------------------
This project - ``cfgclasses`` - aims to solve several issues around the development of command line interfaces (CLIs) in Python using argparse. These issues are:
 * The output from argparse is a typeless namespace allowing ``mypy`` to miss typing bugs
 * Defining a tools CLI using argparse's ``add_argument()`` method involves repetetive boilerplate code

The impact of the type safety issue can be minimised by carefully structuring a tools entry points, however for smaller tools this is often frustrating and distracts from the core functionality of the tool. ``cfgclasses`` provides a 100% type safe interface for defining a tools CLI, and allows the programmer to focus on the structure of the configuration rather than the structure of the CLI.

The boilerplate issue is more of a problem for larger tools, but can be a significant issue for smaller tools as well. Often the structure of this boilerplate code leads to focus on the tools interface, and less on what the configuration structure of the tool is. This can lead to maintainability issues where new options are added without consideration for the impact on the overall configuration structure, resulting in invalid configurations being possible but not being caught. This is a natural outcome of the structure of ``argparse``: the programmer defines the CLI for the tool, and then the namespace is generated from this definition. ``cfgclasses`` reverses this focus: the configuration structure is defined first, and the CLI is generated from this.

Adding to the boilerplate issue is the fact there are common patterns that appear in the usage of argparse's ``add_argument()`` method, yet no central utility methods exist to encapsulate these patterns. In larger projects, utilities can be specified within the project itself for common argument patterns (e.g. file paths, boolean flags, etc), however for smaller projects this is not practical. ``cfgclasses`` aims to provide centralised utilities for common argument patterns.

Similarly, groups of tools which accept similar groups of arguments often duplicate code as building an ``argparse.ArgumentParser`` does not lead to natural code reuse. ``cfgclasses`` uses nested ``dataclass`` definitions (encapsulation), aiming to make code reuse easier and more natural. This same encapsulation also allows for logical grouping of configuration items and methods associated with these items, which can be useful for tools with large numbers of options. 

1.1 Inspiration - ``dataclasses``
'''''''''''''''''''''''''''''''''
The ``dataclasses`` module was introduced in Python 3.7, and provides a decorator that allows the definition of classes with minimal boilerplate. The ``dataclasses`` module is not a replacement for classes, but rather a tool to reduce the boilerplate required to define classes whose primary focus is to define a collection of stored data.

``cfgclasses`` aims to build upon the ``dataclasses`` module to provide a similar interface that allows the definition of classes that represent the configuration of a tool. In the same way that dataclasses for not replace regular classes, ``cfgclasses`` does not aim to replace ``argparse``, but rather to provide a more configuration-structure-first focussed interface for programmers building CLI tools.

1.2 Summary
'''''''''''
In summary, ``cfgclasses`` aims to provide the following:
 * A 100% type safe interface for defining a tools CLI
 * A configuration-structure-first focussed interface for defining a tools CLI
 * Centralised utilities for common argument patterns

``cfgclasses`` does not aim to replace argparse, but to build upon it with the use of the ``dataclasses`` module.

.. note:: 
    The ``cfgclasses`` module is not a replacement for ``argparse`` and there are features of argparse which are not currently, and may never be, supported.

2. Design Overview
------------------
This sections describes the high-level flow of the ``cfgclasses`` module. The subsections then go on to describe each step in the flow in greater detail including descriptions of the key classes and methods involved.

2.1 High-level flow
'''''''''''''''''''

The high-level design of ``cfgclasses`` is as follows:
 * A programmer defines their tools configuration in a class using the ``dataclasses.dataclass`` decorator.
 * The programmer calls the ``cfgclasses.parse_args()`` method on this class with the CLI arguments.
 * The ``parse_args()`` method performs the following internal flow:

   1. Creates a ``Specification`` instance from the class definition.
   2. Builds an ``argparse.ArgumentParser`` instance from the ``Specification`` instance.
   3. Parses the CLI arguments using this ``argparse.ArgumentParser``.
   4. Reads from the ``argparse.Namespace`` output to create an instance of the programmers ``dataclass``.

Note that step (3) is entirely handled by the ``argparse`` module. Steps (1), (2) and (4) are each discussed further in the following subsections.

.. mermaid::

    ---
    title: cfgclasses::parse_args(cls, argv)
    ---
    flowchart LR
        A["`Create a _Specification_`"]:::internal
        B["`Build the _ArgumentParser_`"]:::internal
        C["`Parse CLI into _Namespace_`"]:::external
        D["`Instantiate the _dataclass_`"]:::internal
        A --> B
        B --> C
        C --> D
        classDef internal stroke:#00f,fill:#ddf
        classDef external stroke:#0f0,fill:#dfd


The ``Specification`` class is a representation of the ``dataclass`` definition, where each item of config is expressed by a ``SpecificationItem`` which has attributes mapping directly to the arguments accepted by ``argparse.ArgumentParser.add_argument()``. Creating this specification of the arguments separately from the creation and population of the ``Specification`` benefits the code flow in a number of ways:
 * keeps the most complex logic away from the interaction with ``argparse``, simplifying the code and the testing
 * puts this complex logic in pure functions, further improving the testability
 * simplifies the code path for nested configuration definitions as no branching is required

In addition to this ``parse_args()`` definition, the public API also includes ``ConfigOpts`` and ``NonPositionalConfigOpts`` classes (where the latter is a subclass of the former) which can be used to customize the options for a field in the ``dataclass`` definition. These are stored in the ``dataclasses.field()`` metadata for the field.

Furthermore, a collection of helper functions for common patterns are provided, as well as an ``arg()`` function which creates the ``dataclasses`` field and inserts a ``ConfigOpts`` instance into the metadata in one convenient call. As such, it is expected that a programmer will not need to directly interact with the ``ConfigOpts`` classes, but rather will use the ``arg()`` function and the helper functions. Only when a programmer wants finer control over the ``dataclasses`` field definition will they need to manually create a ``ConfigOpts`` instance.

2.2. Building the specification
'''''''''''''''''''''''''''''''
The ``Specification`` is built from the ``dataclass`` definition by using the ``dataclasses`` module to inspect the class definition and producing a ``SpecificationItem`` for each field in the class, or another ``Specification`` instance for each nested ``dataclass``. @@@ Is this nesting a problem?

.. mermaid::

    ---
    title: Specification Class Diagram
    ---
    classDiagram
        direction LR
        namespace cfgclasses {
            class Specification
            class SpecificationItem
            class StandardSpecItem
            class OptionalSpecItem
            class BoolSpecItem
            class ListSpecItem
            class PositionalSpecItem
            class ListPositionalSpecItem
        }
        class Specification {
            metatype: Type[ToolsConfig]
            members: list[SpecificationItem]
            subspecs: list[Specification]
            add_to_parser(parser: argparse.ArgumentParser)
        }
        class SpecificationItem {
            name: str
            type: Type
            help: str
            metavar: str
            choices: list
            default: Any
            add_to_parser(parser: argparse.ArgumentParser)
            get_optnames() list[str]
            get_kwargs() dict[str, Any]

        }

        ToolsConfig "1" ..o Specification: metatype
        Specification *-- "0..n" SpecificationItem: members
        Specification *-- "0..n" Specification: subspecs

        class StandardSpecItem {
            optnames: list[str]
            get_optnames() list[str]
        }
        SpecificationItem <|-- StandardSpecItem

        class OptionalSpecItem {
            get_kwargs() dict[str, Any]
        }
        StandardSpecItem <|-- OptionalSpecItem

        class BoolSpecItem {
            get_kwargs() dict[str, Any]
        }
        StandardSpecItem <|-- BoolSpecItem

        class ListSpecItem {
            get_kwargs() dict[str, Any]
        }
        StandardSpecItem <|-- ListSpecItem

        class PositionalSpecItem {
            get_optnames() list[str]
            get_kwargs() dict[str, Any]
        }
        SpecificationItem <|-- PositionalSpecItem

        class ListPositionalSpecItem {
            get_kwargs() dict[str, Any]
        }
        PositionalSpecItem <|-- ListPositionalSpecItem

        %% External items
        class ToolsConfig {
            <<dataclass>>
            tool_option_a: int
            tool_option_b: str
        }

        

The ``SpecificationItem`` is an abstract base class consisting of:
 * a name for the field
 * a type for the field
 * an optional help string for the field
 * an optional metavar name for the field
 * an optional list of valid choices for the field
 * an optional default value for the field

It contains the the following methods:
 * ``get_optnames()`` - returns a list of option names
 * ``get_kwargs()`` - returns a dictionary of keyword arguments
 * ``add_to_parser()`` - adds an argument to the given parser using the ``get_optnames()`` and ``get_kwargs()`` methods

There are then several subclasses of ``SpecificationItem`` which are used to represent the different types of fields that can be defined in a ``dataclass`` supported by ``cfgclasses``. These subclasses are:
 * ``StandardSpecItem`` - a standard CLI argument (non-positional)

   * ``OptionalSpecItem`` - an optional argument
   * ``BoolSpecItem`` - a boolean flag such as ``--debug``
   * ``ListSpecItem`` - an argument accepting a list of values

 * ``PositionalSpecItem`` - a positional CLI argument

   * ``ListPositionalSpecItem`` - a positional argument that accepts a list

These classifications of arguments are based on the sets of options to argparse that are required to be set to achieve the appropriate typing and related behavior. See the following section for the details of how these options are set.

2.2.1 Programmer customization
##############################

The programmer can specify the type of the field in the ``dataclass`` definition, and can use the ``default`` and ``default_factory`` options to control the default value given to argparse. However, to customise any other attributes for an entry, or to set an argument as positional, the ``dataclasses.field()`` metadata is used.

The ``dataclasses`` metadata is an untyped dictionary stored on fields, that allows us to store any information we like on a field as well as the built-in values like defaults. ``cfgclasses`` uses a particular entry in this metadata ``cfgclasses.CFG_METADATA_FIELD`` to store a ``ConfigOpts`` or ``NonPositionalConfigOpts`` instance.

These classes allow the following customization:
 * ``help`` - the help string for the argument
 * ``metavar`` - the 'metavar' name to display for the argument
 * ``choices`` - the list of valid choices for the argument

Additionally, the ``NonPositionalConfigOpts`` class allows the user to specify:
 * ``optnames`` - the list of option names for the argument (e.g. ``["-d", "--debug"]``)

If there is no entry in a fields metadata for ``cfgclasses.CFG_METADATA_FIELD`` then the default value of ``NonPositionalConfigOpts`` is used. If an instance of ``ConfigOpts`` is found, then the field is treated as a positional argument.

2.2.2 Programmer argument helper functions
##########################################

Interacting with ``dataclasses`` and creating instances of ``ConfigOpts`` is more verbose than necessary in many cases, so ``cfgclasses`` provides several utilities to improve this.

The ``arg()`` function has the following interface:

.. code-block:: python

    def arg(
        help: str,
        *optnames: str,
        positional: bool = False,
        metavar: Optional[str] = None,
        choices: Optional[list[Any]] = None,
        default: Any = dataclasses.MISSING,
        default_factory: Optional[Callable[[], Any]] = None,
    ) -> dataclasses.Field[Any]:

These arguments are mapped to the equivalent in either ``dataclasses.field()`` for default and default_factory, or to the ``ConfigOpts`` constructor for the other arguments. The ``positional`` argument is used to determine whether to create a ``ConfigOpts`` or ``NonPositionalConfigOpts`` instance, and is ``positional`` is provided then ``optnames`` cannot be specified.


2.3 Populating the ArgumentParser
'''''''''''''''''''''''''''''''''
From the ``Specification``, each member ``SpecificationItem`` is added to the ``ArgumentParser`` using ``add_argument()`` and each nested ``Specification`` is added with ``add_argument_group()``, recursively adding its own members and subspecs to this new group.

The ``ArgOpts`` instance for each ``SpecificationItem`` contains information on the arguments to be passed to ``argparse``. There are some common options which can be set for all arguments, and there are options which are used to control the typing behavior of ``argparse`` to match the expected output types. The common options are:
 * ``type`` - the type of the argument that argparse should parse the argument as
 * ``help`` - the help string for the argument
 * ``metavar`` - the 'metavar' name to display for the argument
 * ``choices`` - the list of valid choices for the argument
 * ``default`` - the default value for the argument

Other than ``type`` all of these are optional and are set by the programmer when defining their ``dataclass`` fields.
The additional option ``dest`` is also commonly used with ``add_argument`` to set the name of the attribute in the ``argparse.Namespace`` that the value of the argument should be stored in. This value matches the name of she ``SpecificationItem``.


The typing considerations are:
 * For lists:

   * ``nargs`` is set to ``"+"`` [#nargs]_
   * ``type`` is the inner type of the list (e.g. ``list[int] -> int``)
   * ``required`` is set to ``True`` if ``default`` is not given

 * For optional types:

   * ``type`` is the inner type of the optional (e.g. ``Optional[int] -> int``)
   * ``required`` is set to ``False``

 * For booleans

   * ``action`` - the action to be taken when the argument is parsed
   * ``type`` - is not given
   * ``required`` is not given

   ``action`` is set to ``store_true`` unless ``default`` is ``True`` in which case the value used is ``store_false`` [#action]_

 * For all other types

   * ``type`` is the type of the argument
   * ``required`` is set to ``True`` if ``default`` is not given

.. [#nargs] other values of ``nargs`` are not supported as they are not known to be necessary configuration focussed view of the CLI.
.. [#action] because of the naming of variables it is recommended not to True as a default value, or to override the option names to negate the flag the user must pass. E.g. ``--no-debug`` for a variable ``debug: bool = arg("Turn off debug", "--no-debug", default=True)``. Even in this example, the mis-match between the help message and the value of the variable is confusing.

2.3.1 Positional options
########################
``cfgclasses`` allows the programmer to specify that any argument is positional, allowing the cli to appear as:

.. code-block:: bash

    $ tool.py positional_arg

instead of:

.. code-block:: bash

    $ tool.py --positional_arg positional_arg

However, this is only possible for regular and ``list`` types, not for ``Optional`` types or booleans. This is because there is no way for a user to specify the ``None`` value to a positional argument for ``Optional`` and argparse does not correctly parse ``True`` or ``False`` strings into booleans. Furthermore, a positional boolean argument is not very useful as a boolean flag is more descriptive with ``--``, e.g. ``tool.py --debug`` rather than the more mysterious ``tool.py True``.

Finally, ``required`` cannot be specified for any positional argument created for argparse.

2.4 Creating the ``dataclass`` instance from the ``argparse.Namespace``
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Once the ``argparse.Namespace`` has been produced it will contain attributes for all the ``SpecificationItem`` instances in the ``Specification`` and its nested subspecs. The attribute names will have been set using the ``dest`` option to ``add_argument()`` to match the name attribute of the ``SpecificationItem``. The values of these attributes will have appropriate types such that they can be directly assigned to the corresponding field in the ``dataclass`` definition.

As such, the ``dataclass`` can be instantiated by iterating over the ``SpecificationItem`` instances and assigning the value of the corresponding attribute in the ``argparse.Namespace`` to the field in the ``dataclass``. For nested configuration, we simply need to perform this operation depth-first so that we build the nested configuration instances and assign them to the correct fields in the parent configuration instance.


2.5 Summary
'''''''''''
The ``parse_args()`` method of the ``cfgclasses`` module performs the following steps:
 * Creates a ``Specification`` instance from the ``dataclass`` definition
 * Builds an ``argparse.ArgumentParser`` instance from the ``Specification`` instance
 * Parses the CLI arguments using this ``argparse.ArgumentParser``
 * Reads from the ``argparse.Namespace`` output to create an instance of the programmers ``dataclass``

The bulk of the complexity is in the creation of the ``SpecificationItem`` instances as there is a combination of logic based on the type of the fields and the users options for the field to be processed.



Additional Feature Designs
-----------------------------

There are additional features of the module that have their own design pages as listed below. These pages are expansions on this original design that build upon the core principles and design aspects covered here.

.. toctree::
    :maxdepth: 1
    :glob:

    designs/*
