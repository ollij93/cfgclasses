Transforms
==========

1. Problem Definition
---------------------
A tools configuration is sometimes limited by the requirement that it can be built from the CLI arguments.
For example, a tool may want to be configured with a ``set`` of file paths, but the CLI only supports building ``list`` types. 
Therefore, there is often a desire to transform a configuration option from one value to another ahead of running the primary flow of the tool.

A common example of a transformation is reading the contents of a file.
Many tools will accept a file path as a CLI argument, which is immediately opened, its content read, and then the file is closed on not used again.
This is a common pattern and can be abstracted into a reusable transformation: ``file_content(path: str) -> str``.

In more complex examples, a particular file format may be expected, and have its own transformation. For example json files can use ``json_content(path: str) -> dict[str, Any]``. Similar transformations can be defined for other file formats, such as CSV, yaml, pickle, etc.

A note on defaults and choices etc.
###################################
These transformations are limited to operation on the value read from the CLI. When constructing an instance of the ConfigClass through other mechanisms (such as the constructed provided by ``dataclasses``) the transformation is not applied.

In order to support configuration options whose types match those of the CLI arguments (e.g. choices) the typing of those options must be updated to match the transformation (input) type.
E.g. a transformation that accepts an ``int`` and returns a ``str`` would require the choices to be a list of ``int`` values, not their string representations.

For ``default`` and ``default_factory`` values this is further complicated by the fact that these values are stored directly in the ``dataclasses`` field.
To maintain the typing correctly, the default value must be transformed before being assigned to the field.
Similarly, the ``default_factory`` must be stored in the ``dataclasses`` field as a function that returns the transformed value. I.e. ``default_factory = lambda: transform(factory())``.

Unfortunately, this means that ``cfgclasses`` will separately have to store the _raw_ ``default`` value, since the un-transformed value needs to be specified to ``argparse``.
Note however, that a ``default_factory`` value does not need to stored, as this is not supported by ``argparse``, so if ``default_factory`` is used it can be called and assigned to the ``default`` value instead.

2. Solution
-----------
``cfgclasses`` allows the specification of a transformation function for a particular configuration option.
The transformation function accepts a single argument or type ``T`` and returns a value of type ``U``.
The configuration option must also be of type ``U``, and type ``T`` must be type supported by ``cfgclasses`` arguments (simple types like ``str`` or ``int``; ``list`` of simple types; or ``Optional`` of simple types).

Ideally a transformation function is strongly typed and ``cfgclasses`` and ``mypy`` would be capable of inferring the types ``T`` and ``U``.
However, functions can be permissive with their inputs (e.g. ``Iterable[str]``) where ``cfgclasses`` would require a stricted type (``list[str]``).
Furthermore, the use of ``lambda`` functions as transforms or the use of other untyped functions would mean inspecting the transform function for its typing would be difficult.

Therefore, a type for the input to the transformation must also be specified.

Class transformations
#####################
In addition to the above, it is also sometimes desirable to transform a group of configuration options into a single instance of another type.

For example, in the popular example case of specifying the logging level, it is common to have a ``--debug`` option and the mutually-exclusive ``--quiet`` option.
These options can then be used to set the logging level to ``DEBUG`` or ``ERROR`` respectively, with the default being ``INFO``.
Without the use of transforms, the config class definition would look like so:

.. code-block:: python

    @dataclass
    class LoggingConfig(MutuallyExclusiveConfigClass):
        debug: bool = arg("Enable debug logging")
        quiet: bool = arg("Disable info logging")

        def log_level(self) -> int:
            if self.debug:
                return logging.DEBUG
            elif self.quiet:
                return logging.ERROR
            else:
                return logging.INFO

    @dataclass
    class Config(ConfigClass):
        log_level: LoggingConfig

While this pattern is sufficient, it does have one major drawback: When manually constructing an instance of ``Config``, e.g. during testing, an invalid combination of ``debug`` and ``quiet`` can be used.

.. code-block:: python

    config = Config(LoggingConfig(debug=True, quiet=True))

In this situation, the behavior depends on which of the ``debug`` or ``quiet`` modes is checked first in the ``log_level()`` method.

With the use of a class transform, this problem can be avoided.

.. code-block:: python

    @dataclass
    class LoggingConfig(MutuallyExclusiveConfigClass):
        debug: bool = arg("Enable debug logging")
        quiet: bool = arg("Disable info logging")

        def log_level(self) -> int:
            if self.debug:
                return logging.DEBUG
            elif self.quiet:
                return logging.ERROR
            else:
                return logging.INFO

    @dataclass
    class Config(ConfigClass):
        log_level: int = cfgtransform(LoggingConfig, LoggingConfig.log_level)

In this case, the ``log_level`` configuration option is transformed from a ``LoggingConfig`` instance to an ``int`` using the ``LoggingConfig.log_level`` function used previously.
While it is still possible to construct invalid instances of ``LoggingConfig``, it is no longer possible to construct an invalid instance of ``Config`` itself.

Another pattern where these transform are useful is constructing more complex classes from simple ConfigClass definitions.
Often a class definition may be out of the programmers control (e.g. part of a third party library) or the required functionality may mean that usage of a dataclass is not possible.
In these cases, the programmer can define a simple ConfigClass with options sufficient to then build the more complex class from.

.. code-block:: python

    class NotADataClass:
        def __init__(self, a: int, b: str):
            self.a = a
            self.b = b

    @dataclass
    class DataClassConfig(ConfigClass):
        a: int = arg("An int")
        b: str = arg("A string")

        def to_not_a_dataclass(self) -> NotADataClass:
            return NotADataClass(self.a, self.b)

    @dataclass
    class Config(ConfigClass):
        not_a_dataclass: NotADataClass = cfgtransform(
            DataClassConfig,
            DataClassConfig.to_not_a_dataclass,
        )


3. Design ammendments
---------------------
The following changes are made to the design to support transformations:

* The ``arg()`` and ``optional()`` functions are updated to accept this transformation function as an optional argument. The typing of the functions is also updated to reflect the use of the transformation.
* These functions are also updated to accept the transformation type as an argument
* The ``ConfigOpts`` class is updated to contain transformation function and transformation type members and is made to be Generic over the appropriate types, maintaining the type safety when using the transformations.
* The ``ConfigOpts`` is also used to store the default value as this is now distinct from the value stored in the ``dataclasses`` field.
* When building the ``Specification`` for a ``ConfigClass`` the transformation function and type are extracted from the ``ConfigOpts`` class and stored in the ``Specification``.

  * If not specified, the transformation function is set to the identity function and the transformation type is set to the type of the configuration option.
* To build the ``ConfigClass`` from the CLI arguments, instead of directly assigning the value from the ``argparse.Namespace`` the transformation function is invoked with the value from the ``argparse.Namespace``.

For the class transformation, the following changes are made:

* A new ``cfgtransform()`` function is added which takes a type and a transform function.
* A new ``ConfigClassTransform`` type is defined to contain the type and transform function for classes.
* The ``Specification`` is updated to check for this class in the dataclass metadata and store the transform information.
* When building the ``ConfigClass`` from the CLI arguments, the transforms of each of its subspecs are invoked to apply the transformations.

4. Implementation and testing
-----------------------------
Type safety is key point to be maintained with this change.
It would be easy to overlook during implementation and testing with excessive use of the Any type.

Additional testing is to be implemented to ensure that the type safety is maintained.
This includes test cases where mypy would fail due to transform functions and types being incompatible.
This is an unusual testing pattern, but is required to verify and maintain that typing bugs are not introduced through this change or any future additions.
