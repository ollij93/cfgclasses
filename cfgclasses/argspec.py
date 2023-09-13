"""Module for defining the argument specification for a ConfigClass."""
import abc
import argparse
import dataclasses
from typing import (
    Any,
    Callable,
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
    "ConfigClassTransform",
    "NonPositionalConfigOpts",
)

#:Key in the dataclasses field metadata to store the ConfigOpts in.
CFG_METADATA_FIELD = "cfgclasses.configopts"

_T = TypeVar("_T")
_U = TypeVar("_U")
_ConfigGroupT = TypeVar("_ConfigGroupT", bound=ConfigGroup)


#:Identity function for use as a default transform.
def identity_transform(value: _T) -> _T:
    """Identity function for use as a default transform."""
    return value


class NotSpecified:
    """Type for unspecified argument specifiers"""

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, NotSpecified)


@dataclasses.dataclass
class ConfigOpts(Generic[_T, _U]):
    """
    Data stored in a dataclass field's metadata for customizing CLI options.
    """

    #: Help string for the argument.
    help: str = dataclasses.field(default="")
    #: Name to display for the argument in usage messages.
    metavar: Optional[str] = dataclasses.field(default=None)
    #: List of valid choices for the argument.
    choices: Optional[Iterable[_T]] = dataclasses.field(default=None)
    #: Transform function to modify the argument value after parsing the CLI.
    transform: Optional[Callable[[_T], _U]] = dataclasses.field(default=None)
    #: Input type to apply to the CLI argument before transforming.
    transform_type: Optional[Type[_T]] = dataclasses.field(default=None)
    #: Default value for the argument if not provided on the CLI.
    #: This is separate from the default and default_factory stored on the
    #: dataclasses field as when working with transforms this value is the
    #: un-transformed value of the default.
    default: _T | NotSpecified = dataclasses.field(
        default_factory=NotSpecified
    )


@dataclasses.dataclass
class NonPositionalConfigOpts(ConfigOpts[_T, _U]):
    """
    Config options for a non-positional argument.
    """

    #: List of alternative names (such as ``["-f", "--force"]``) for the argument.
    optnames: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ConfigClassTransform(Generic[_ConfigGroupT, _U]):
    """
    Data stored in a dataclass field's metadata for transforming config classes.
    """

    #: Transform function to modify the CLI values after parsing.
    transform: Callable[[_ConfigGroupT], _U]
    #: Input type to build the CLI from before transforming.
    transform_type: Type[_ConfigGroupT]


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
class SpecificationItem(abc.ABC, Generic[_T]):
    """
    Specification for a single argument to be passed to
    argparse.ArgumentParser.add_argument().
    """

    #: Name of the argument used as "--name" on the command line.
    name: str
    #: Type the argument should be converted to by argparse.
    type: Type[Any]
    #: Help string to display for the argument.
    help: str
    #: Metavar to display for the argument in the help message.
    metavar: Optional[str]
    #: List of valid choices for the argument.
    choices: Optional[Iterable[Any]]
    #: Default value for the argument if not provided on the CLI.
    default: Any
    #: Transform function
    transform: Callable[[Any], _T]

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
    def get_argtype(cls, field_type: Type[Any]) -> Type[Any]:
        """Get the type to use with argparse for this field."""
        # Default is just the field_type - but can be overridden e.g. for lists
        return field_type

    def add_to_parser(self, parser: argparse._ActionsContainer) -> None:
        """Add this argument to the given parser."""
        parser.add_argument(
            *self.get_optnames(),
            **self.get_kwargs(),
        )

    def extract_value_from_namespace(
        self, namespace: argparse.Namespace
    ) -> Any:
        """Extract the value of this argument from the given namespace."""
        return self.transform(getattr(namespace, self.name))


@dataclasses.dataclass
class StandardSpecItem(SpecificationItem[_T]):
    """
    A non-positional argument specification item.
    """

    #: List of alternative names (such as -f or --force) for the argument.
    #: If an empty list the name of the specification item is used with any
    #: underscores replaced with hyphens.
    optnames: list[str]

    @classmethod
    def from_field(
        cls,
        metadata: NonPositionalConfigOpts[Any, _T],
        field: dataclasses.Field[Any],
    ) -> "SpecificationItem[_T]":
        """Instantiate an instance of this class from the field definition."""
        return cls(
            field.name,
            cls.get_argtype(metadata.transform_type or field.type),
            metadata.help,
            metadata.metavar,
            metadata.choices,
            _default_from_field(field),
            metadata.transform or identity_transform,
            metadata.optnames,
        )

    def get_optnames(self) -> list[str]:
        return self.optnames or [f"--{self.name.replace('_', '-')}"]


@dataclasses.dataclass
class ListSpecItem(StandardSpecItem[_T]):
    """
    A non-positional argument specification item that takes a list of values.
    """

    def get_kwargs(self) -> dict[str, Any]:
        return super().get_kwargs() | {"nargs": "+"}

    @classmethod
    def get_argtype(cls, field_type: Type[Any]) -> Type[Any]:
        # For lists, the type is the type of the list elements
        return get_args(field_type)[0]  # type: ignore


@dataclasses.dataclass
class OptionalSpecItem(StandardSpecItem[_T]):
    """A non-positional argument specification item that is optional."""

    def get_kwargs(self) -> dict[str, Any]:
        return super().get_kwargs() | {"required": False}

    @classmethod
    def get_argtype(cls, field_type: Type[Any]) -> Type[Any]:
        # For Optional types, the type is the type of the optional value
        return get_args(field_type)[0]  # type: ignore


@dataclasses.dataclass
class BoolSpecItem(StandardSpecItem[_T]):
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


class PositionalSpecItem(SpecificationItem[_T]):
    """A positional argument specification item."""

    def get_optnames(self) -> list[str]:
        return [self.name]

    @classmethod
    def from_field(
        cls, metadata: ConfigOpts[Any, _T], field: dataclasses.Field[Any]
    ) -> "SpecificationItem[_T]":
        """Instantiate an instance of this class from the field definition."""
        return cls(
            field.name,
            cls.get_argtype(metadata.transform_type or field.type),
            metadata.help,
            metadata.metavar,
            metadata.choices,
            _default_from_field(field),
            metadata.transform or identity_transform,
        )

    def get_kwargs(self) -> dict[str, Any]:
        ret = super().get_kwargs()
        # Don't specify dest or required for positional arguments
        del ret["dest"]
        # Don't specify required as theirs implicitly a default
        if "required" in ret:
            del ret["required"]
        return ret


class ListPositionalSpecItem(PositionalSpecItem[_T]):
    """A positional argument specification item that takes a list of values."""

    def get_kwargs(self) -> dict[str, Any]:
        return super().get_kwargs() | {"nargs": "+"}

    @classmethod
    def get_argtype(cls, field_type: Type[Any]) -> Type[Any]:
        # For lists, the type is the type of the list elements
        return get_args(field_type)[0]  # type: ignore


def _specitem_from_field(
    field: dataclasses.Field[Any],
) -> "SpecificationItem[Any]":
    """Instantiate an instance of SpecificationItem from the field definition."""
    metadata: ConfigOpts[Any, Any] = field.metadata.get(
        CFG_METADATA_FIELD, NonPositionalConfigOpts()
    )
    field_type = metadata.transform_type or field.type
    ret: SpecificationItem[Any]
    if isinstance(metadata, NonPositionalConfigOpts):
        # Handle the creation of the standard specification item
        if get_origin(field_type) == list:
            ret = ListSpecItem.from_field(metadata, field)
        elif _is_optional_type(field_type):
            ret = OptionalSpecItem.from_field(metadata, field)
        elif field_type == bool:
            ret = BoolSpecItem.from_field(metadata, field)
        else:
            ret = StandardSpecItem.from_field(metadata, field)
    else:
        # Handle the creation of the positional specification item
        if get_origin(field_type) == list:
            ret = ListPositionalSpecItem.from_field(metadata, field)
        elif get_origin(field_type) is None:
            ret = PositionalSpecItem.from_field(metadata, field)
        else:
            raise TypeError(
                f"Can't use type {field_type} with a positional argument."
            )

    return ret


def _is_configcls_field(field: dataclasses.Field[Any]) -> bool:
    """Check if the given field is a ConfigClass typed field."""
    extraconfig = field.metadata.get(CFG_METADATA_FIELD)
    if isinstance(extraconfig, ConfigClassTransform):
        return True
    try:
        return issubclass(field.type, ConfigGroup)
    except TypeError:
        return False


def _spec_from_field(
    field: dataclasses.Field[Any],
) -> "Specification[Any]":
    """Instantiate an instance of a Specification from the field definition."""
    type_ = field.type
    extraconfig = field.metadata.get(CFG_METADATA_FIELD)
    if isinstance(extraconfig, ConfigClassTransform):
        type_ = extraconfig.transform_type

    return Specification.from_class(
        type_,
        extraconfig.transform if extraconfig else None,
    )


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
    members: list[SpecificationItem[Any]]
    #: Mapping of spec names to Specification for any subspecs of this spec.
    subspecs: dict[str, "Specification[Any]"]
    #: The transform to be applied to this specification
    transform: Optional[Callable[[_ConfigGroupT], Any]]

    @staticmethod
    def from_class(
        metatype: Type[_ConfigGroupT],
        cfgtransform: Optional[Callable[[_ConfigGroupT], Any]] = None,
    ) -> "Specification[_ConfigGroupT]":
        """Instantiate an instance of this class from the ConfigGroup class"""
        return Specification(
            metatype,
            [
                _specitem_from_field(field)
                for field in dataclasses.fields(metatype)
                if not _is_configcls_field(field)
            ],
            {
                field.name: _spec_from_field(field)
                for field in dataclasses.fields(metatype)
                if _is_configcls_field(field)
            },
            cfgtransform if cfgtransform else None,
        )

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
                item.name: item.extract_value_from_namespace(namespace)
                for item in self.members
            }
            | {
                subspec_name: (subspec.transform or (lambda x: x))(
                    subspec.construct_from_namespace(namespace)
                )
                for subspec_name, subspec in self.subspecs.items()
            }
        )
