# Config Classes

Strongly typed tool configuration classes for argument parsing.

Config classes are representations of a python tools CLI configuration options
built on dataclasses. This allows individual tools to focus on specifying their
configuration structure without the overhead of interacting with argparse and
the typeless Namespace it returns.
