"""Module for defining the argument specification for a ConfigClass."""
import abc
import argparse
import dataclasses
from typing import (
    Any,
    Generic,
    Iterable,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from .configgroup import ConfigGroup

__all__ = (
    "CFG_METADATA_FIELD",
    "ConfigOpts",
    "NonPositionalConfigOpts",
)

#:Key in the dataclasses field metadata to store the ConfigOpts in.
CFG_METADATA_FIELD = "cfgclasses.configopts"

_T = TypeVar("_T")
_ConfigGroupT = TypeVar("_ConfigGroupT", bound=ConfigGroup)


@dataclasses.dataclass
class ConfigOpts:
    """
    Data stored in a dataclass field's metadata for customizing CLI options.
    """

    #: Help string for the argument.
    help: str = dataclasses.field(default="")
    #: Name to display for the argument in usage messages.
    metavar: Optional[str] = dataclasses.field(default=None)
    #: List of valid choices for the argument.
    choices: Optional[Iterable[Any]] = dataclasses.field(default=None)


@dataclasses.dataclass
class NonPositionalConfigOpts(ConfigOpts):
    """
    Config options for a non-positional argument.
    """

    #: List of alternative names (such as ``["-f", "--force"]``) for the argument.
    optnames: list[str] = dataclasses.field(default_factory=list)


class NotSpecified:
    """Type for unspecified argument specifiers"""

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, NotSpecified)


def _default_from_field(field: dataclasses.Field[_T]) -> _T | NotSpecified:
    """Determine the default value for the field."""
    if field.default is not dataclasses.MISSING:
        return field.default
    if field.default_factory is not dataclasses.MISSING:
        return field.default_factory()
    return NotSpecified()


def _is_optional_type(metatype: Type[Any]) -> bool:
    """Check if the given type is an Optional type."""
    type_args = get_args(metatype)
    return (
        get_origin(metatype) == Union
        and len(type_args) == 2
        and type(None) in type_args
    )


@dataclasses.dataclass
class SpecificationItem(abc.ABC):
    """
    Specification for a single argument to be passed to
    argparse.ArgumentParser.add_argument().
    """

    #: Name of the argument used as "--name" on the command line.
    name: str
    #: Type the argument should be converted to by argparse.
    type: Type[Any]
    #: Help string to display for the argument.
    help: str = dataclasses.field(default="")
    #: Metavar to display for the argument in the help message.
    metavar: Optional[str] = dataclasses.field(default=None)
    #: List of valid choices for the argument.
    choices: Optional[Iterable[Any]] = dataclasses.field(default=None)
    #: Default value for the argument if not provided on the CLI.
    default: Any | NotSpecified = dataclasses.field(
        default_factory=NotSpecified
    )

    @abc.abstractmethod
    def get_optnames(self) -> list[str]:
        """Get the optnames for this argument."""

    def get_kwargs(self) -> dict[str, Any]:
        """Get the kwargs for this argument."""
        return (
            {
                "dest": self.name,
                "type": self.type,
                "help": self.help,
            }
            | ({"metavar": self.metavar} if self.metavar is not None else {})
            | ({"choices": self.choices} if self.choices is not None else {})
            | (
                # Only give argparse the default if it is specified as None is a
                # valid value for a default
                {"default": self.default}
                if self.default != NotSpecified()
                else {"required": True}
            )
        )

    @classmethod
    def get_type_from_field(cls, field: dataclasses.Field[Any]) -> Type[Any]:
        """Get the type to use with argparse for this field."""
        # Default is just the field.type - but can be overridden e.g. for lists
        return field.type

    def add_to_parser(self, parser: argparse._ActionsContainer) -> None:
        """Add this argument to the given parser."""
        parser.add_argument(
            *self.get_optnames(),
            **self.get_kwargs(),
        )


@dataclasses.dataclass
class StandardSpecItem(SpecificationItem):
    """
    A non-positional argument specification item.
    """

    #: List of alternative names (such as -f or --force) for the argument.
    #: If an empty list the name of the specification item is used with any
    #: underscores replaced with hyphens.
    optnames: list[str] = dataclasses.field(default_factory=list)

    @classmethod
    def from_field(
        cls, metadata: NonPositionalConfigOpts, field: dataclasses.Field[Any]
    ) -> "SpecificationItem":
        """Instantiate an instance of this class from the field definition."""
        return cls(
            field.name,
            cls.get_type_from_field(field),
            metadata.help,
            metadata.metavar,
            metadata.choices,
            _default_from_field(field),
            metadata.optnames,
        )

    def get_optnames(self) -> list[str]:
        return self.optnames or [f"--{self.name.replace('_', '-')}"]


@dataclasses.dataclass
class ListSpecItem(StandardSpecItem):
    """
    A non-positional argument specification item that takes a list of values.
    """

    def get_kwargs(self) -> dict[str, Any]:
        return super().get_kwargs() | {"nargs": "+"}

    @classmethod
    def get_type_from_field(cls, field: dataclasses.Field[Any]) -> Type[Any]:
        # For lists, the type is the type of the list elements
        return get_args(field.type)[0]  # type: ignore


@dataclasses.dataclass
class OptionalSpecItem(StandardSpecItem):
    """A non-positional argument specification item that is optional."""

    def get_kwargs(self) -> dict[str, Any]:
        return super().get_kwargs() | {"required": False}

    @classmethod
    def get_type_from_field(cls, field: dataclasses.Field[Any]) -> Type[Any]:
        # For Optional types, the type is the type of the optional value
        return get_args(field.type)[0]  # type: ignore


@dataclasses.dataclass
class BoolSpecItem(StandardSpecItem):
    """A non-positional argument specification item that is a boolean."""

    def get_kwargs(self) -> dict[str, Any]:
        action = "store_true"
        if self.default is True:
            action = "store_false"
        ret = super().get_kwargs() | {"action": action}
        # Don't specify type for boolean flags as theirs nothing to convert
        del ret["type"]
        # Don't specify required as theirs implicitly a default
        if "required" in ret:
            del ret["required"]
        return ret


class PositionalSpecItem(SpecificationItem):
    """A positional argument specification item."""

    def get_optnames(self) -> list[str]:
        return [self.name]

    @classmethod
    def from_field(
        cls, metadata: ConfigOpts, field: dataclasses.Field[Any]
    ) -> "SpecificationItem":
        """Instantiate an instance of this class from the field definition."""
        return cls(
            field.name,
            cls.get_type_from_field(field),
            metadata.help,
            metadata.metavar,
            metadata.choices,
            _default_from_field(field),
        )

    def get_kwargs(self) -> dict[str, Any]:
        ret = super().get_kwargs()
        # Don't specify dest or required for positional arguments
        del ret["dest"]
        # Don't specify required as theirs implicitly a default
        if "required" in ret:
            del ret["required"]
        return ret


class ListPositionalSpecItem(PositionalSpecItem):
    """A positional argument specification item that takes a list of values."""

    def get_kwargs(self) -> dict[str, Any]:
        return super().get_kwargs() | {"nargs": "+"}

    @classmethod
    def get_type_from_field(cls, field: dataclasses.Field[Any]) -> Type[Any]:
        # For lists, the type is the type of the list elements
        return get_args(field.type)[0]  # type: ignore


def specitem_from_field(field: dataclasses.Field[Any]) -> "SpecificationItem":
    """Instantiate an instance of this class from the field definition."""
    metadata: ConfigOpts = field.metadata.get(
        CFG_METADATA_FIELD, NonPositionalConfigOpts()
    )
    ret: SpecificationItem
    if isinstance(metadata, NonPositionalConfigOpts):
        # Handle the creation of the standard specification item
        if get_origin(field.type) == list:
            ret = ListSpecItem.from_field(metadata, field)
        elif _is_optional_type(field.type):
            ret = OptionalSpecItem.from_field(metadata, field)
        elif field.type == bool:
            ret = BoolSpecItem.from_field(metadata, field)
        else:
            ret = StandardSpecItem.from_field(metadata, field)
    else:
        # Handle the creation of the positional specification item
        if get_origin(field.type) == list:
            ret = ListPositionalSpecItem.from_field(metadata, field)
        elif get_origin(field.type) is None:
            ret = PositionalSpecItem.from_field(metadata, field)
        else:
            raise TypeError(
                f"Can't use type {field.type} with a positional argument."
            )

    return ret


def _is_configcls(type_: Any) -> bool:
    """Check if the given type is a ConfigClass"""
    try:
        return issubclass(type_, ConfigGroup)
    except TypeError:
        return False


@dataclasses.dataclass
class Specification(Generic[_ConfigGroupT]):
    """
    Representation of a ConfigClass in format suitable to pass to argparse.

    This specification maps to an ArgumentGroup in argparse, each member
    SpecificationItem a call to add_argument() and each subspec another
    ArgumentGroup added with add_argument_group().
    """

    #: The ConfigClass type this specification describes.
    metatype: Type[_ConfigGroupT]
    #: List of SpecificationItems for the members of this group.
    members: list[SpecificationItem] = dataclasses.field(default_factory=list)
    #: Mapping of spec names to Specification for any subspecs of this spec.
    subspecs: dict[str, "Specification[Any]"] = dataclasses.field(
        default_factory=dict
    )

    @staticmethod
    def from_class(
        metatype: Type[_ConfigGroupT],
    ) -> "Specification[_ConfigGroupT]":
        """Instantiate an instance of this class from the ConfigGroup class"""
        spec = Specification(metatype)
        for field in dataclasses.fields(metatype):
            if _is_configcls(field.type):
                spec.subspecs[field.name] = Specification.from_class(
                    field.type
                )
            else:
                spec.members.append(specitem_from_field(field))
        return spec

    def add_to_parser(self, parser: argparse._ActionsContainer) -> None:
        """Add this argument group to the given parser."""
        group = self.metatype.add_argument_group(parser)
        for member in self.members:
            member.add_to_parser(group)
        for subspec in self.subspecs.values():
            subspec.add_to_parser(group)

    def construct_from_namespace(
        self, namespace: argparse.Namespace
    ) -> _ConfigGroupT:
        """Construct an instance of the ConfigClass from the given namespace."""
        return self.metatype(
            **{
                item.name.replace("-", "_"): getattr(namespace, item.name)
                for item in self.members
            }
            | {
                subspec_name: subspec.construct_from_namespace(namespace)
                for subspec_name, subspec in self.subspecs.items()
            }
        )
