"""Module for defining the argument specification for a ConfigClass."""
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

CFG_METADATA_FIELD = "cfgclasses.configopts"

_T = TypeVar("_T")
_ConfigGroupT = TypeVar("_ConfigGroupT", bound=ConfigGroup)


# If custom optnames are specified, they can be specified as a list of strings
# otherwise this is a boolean indicating whether the argument is positional
# (If positional, optnames cannot be specified so if this is a list the argument
# is not positional)
OptNamesOrPos = Union[list[str], bool]


@dataclasses.dataclass
class ConfigOpts:
    """
    Data stored in a dataclass field's metadata for customizing CLI options.

    ..attribute:: help
        Help string for the argument.
    ..attribute:: optnamesorpos
        List of names (such as -f or --force) for the argument.
        Alternatively, if this is a boolean, it indicates whether the argument is positional.
        If a list, the argument is not positional.
    ..attribute:: metavar
        Name to display for the argument in usage messages.
    ..attribute:: choices
        List of valid choices for the argument.
    ..attribute:: nargs
        Number of arguments to consume. E.g. 1, "+", "*", etc.
        Should only be set for list types.
    """

    help: str = dataclasses.field(default="")
    optnamesorpos: OptNamesOrPos = dataclasses.field(default=False)
    metavar: Optional[str] = dataclasses.field(default=None)
    choices: Optional[Iterable[Any]] = dataclasses.field(default=None)
    nargs: Optional[Union[int, str]] = dataclasses.field(default=None)


class NotSpecified:
    """Type for unspecified argument specifiers"""

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, NotSpecified)


def _none_to_notspec(value: _T | None) -> _T | NotSpecified:
    """Convert None to NotSpecified."""
    if value is None:
        return NotSpecified()
    return value


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


def _aptype_from_metatype(metatype: Type[Any]) -> Type[Any]:
    """Convert a metatype to the type arg used by argparse."""
    # For lists, simply remove the list wrapper - nargs is used to create the list
    if get_origin(metatype) == list:
        return get_args(metatype)[0]  # type: ignore
    # For `Optional[type]` just remove the Optional wrapper - the None value
    # is automatically included by argparse. The use of required and
    # defaults will also impact this.
    if _is_optional_type(metatype):
        return [a for a in get_args(metatype) if a is not None][0]  # type: ignore
    # No other type wrappers are currently supported
    if get_origin(metatype) is not None:
        raise TypeError(
            f"Can't handle metatype {get_origin(metatype)} of {metatype}"
        )
    # For all remaining types, just leave the type for argparse to deal with
    return metatype


def _nargs_from_metadata(
    metadata: ConfigOpts, metatype: Type[Any]
) -> int | str | NotSpecified:
    """Determine the nargs value from the metadata and metatype."""
    if get_origin(metatype) == list:
        # Allow users to override nargs, e.g. to go from "+" -> "*" if empty
        # lists are permitted
        return metadata.nargs or "+"

    if metadata.nargs is not None:
        raise TypeError(f"Can't handle nargs for non-list type {metatype}")

    return NotSpecified()


@dataclasses.dataclass
class ArgOpts:
    """
    Options for an argument to be passed to
    argparse.ArgumentParser.add_argument().

    ..attribute:: help
        Help string for the argument.
    ..attribute:: metatype
        Type of the field this argument is for, e.g. Optional[str], list[int], etc.
    ..attribute:: type
        Type of the argument given to argparse. E.g. int, str, etc.
    ..attribute:: default
        Default value for the argument.
    ..attribute:: metavar
        Name to display for the argument in usage messages.
    ..attribute:: choices
        List of valid choices for the argument.
    ..attribute:: action
        Action to take when the argument is encountered. E.g. "store_true"
    .. attribute:: nargs
        Number of arguments to consume. E.g. 1, "+", "*", etc.
    """

    help: str
    metatype: Any
    type: Type[Any]
    default: Any = dataclasses.field(default_factory=NotSpecified)
    metavar: str | NotSpecified = dataclasses.field(
        default_factory=NotSpecified
    )
    choices: Iterable[Any] | NotSpecified = dataclasses.field(
        default_factory=NotSpecified
    )
    action: str | NotSpecified = dataclasses.field(
        default_factory=NotSpecified
    )
    nargs: Union[int, str] | NotSpecified = dataclasses.field(
        default_factory=NotSpecified
    )

    def required(self, positional: bool) -> bool:
        """Determine whether the "required" flag should be set."""
        return not (
            _is_optional_type(self.metatype)
            or positional
            or self.default != NotSpecified()
        )

    def to_kwargs(self, positional: bool) -> dict[str, Any]:
        """Convert to kwargs for argparse.ArgumentParser.add_argument()"""
        return {
            k: v
            for k, v in dataclasses.asdict(self).items()
            # Don't output unset values or the metavar
            if not isinstance(v, NotSpecified) and k != "metatype"
            # Don't specify type when using "store_true" action
            and (k != "type" or self.action != "store_true")
        } | ({"required": True} if self.required(positional) else {})

    @staticmethod
    def from_field(
        metatype: Type[Any], metadata: ConfigOpts, default: Any
    ) -> "ArgOpts":
        """Instantiate an instance of this class from the field definition."""
        return ArgOpts(
            metadata.help,
            metatype=metatype,
            type=_aptype_from_metatype(metatype),
            default=default,
            metavar=_none_to_notspec(metadata.metavar),
            choices=_none_to_notspec(metadata.choices),
            nargs=_nargs_from_metadata(metadata, metatype),
            # For boolean types that do not default to true, use the
            # 'store_true' action allowing flags like `--debug` to be used
            # rather than `--debug True`
            action=(
                "store_true"
                if metatype == bool and default is not True
                else NotSpecified()
            ),
        )


@dataclasses.dataclass
class SpecificationItem:
    """
    Specification for a single argument to be passed to
    argparse.ArgumentParser.add_argument().

    ..attribute:: name
        Name of the argument used as "--name" on the command line.
    ..attribute:: optnames
        List of names (such as -f or --force) for the argument.
        If None, the argument is positional.
    ..attribute:: opts
        ArgOpts instance containing the options for the argument.
    """

    name: str
    optnames: Optional[list[str]]
    opts: ArgOpts

    @staticmethod
    def from_field(field: dataclasses.Field[Any]) -> "SpecificationItem":
        """Instantiate an instance of this class from the field definition."""
        metadata: ConfigOpts = field.metadata.get(
            CFG_METADATA_FIELD, ConfigOpts()
        )

        opts = ArgOpts.from_field(
            field.type, metadata, _default_from_field(field)
        )
        name = field.name.replace("_", "-")
        optnames = (
            metadata.optnamesorpos
            if isinstance(metadata.optnamesorpos, list)
            else None
            if metadata.optnamesorpos
            else []
        )
        return SpecificationItem(
            name,
            optnames,
            opts,
        )

    def add_to_parser(self, parser: argparse._ActionsContainer) -> None:
        """Add this argument to the given parser."""
        kwargs: dict[str, Any] = {}
        if self.optnames is not None:
            kwargs["dest"] = self.name
        parser.add_argument(
            *(
                [self.name]
                if self.optnames is None
                else (self.optnames or [f"--{self.name}"])
            ),
            **(kwargs | self.opts.to_kwargs(self.optnames is None)),
        )


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

    .. attribute:: metatype
        The ConfigClass type this specification describes.
    .. attribute:: members
        List of SpecificationItems for the members of this group.
    .. attribute:: subspecs
        Mapping of spec names to Specification for any subspecs of this spec.
    .. attribute:: is_mutually_exclusive
        Whether this group is mutually exclusive.
    """

    metatype: Type[_ConfigGroupT]
    members: list[SpecificationItem] = dataclasses.field(default_factory=list)
    subspecs: dict[str, "Specification[Any]"] = dataclasses.field(
        default_factory=dict
    )
    is_mutually_exclusive: bool = dataclasses.field(default=False)

    @staticmethod
    def from_class(
        metatype: Type[_ConfigGroupT], is_mutually_exclusive: bool = False
    ) -> "Specification[_ConfigGroupT]":
        """Instantiate an instance of this class from the ConfigGroup class"""
        spec = Specification(
            metatype, is_mutually_exclusive=is_mutually_exclusive
        )
        for field in dataclasses.fields(metatype):
            if _is_configcls(field.type):
                spec.subspecs[field.name] = Specification.from_class(
                    field.type,
                    field.metadata.get("mutually_exclusive", False),
                )
            else:
                spec.members.append(SpecificationItem.from_field(field))
        return spec

    def add_to_parser(self, parser: argparse._ActionsContainer) -> None:
        """Add this argument group to the given parser."""
        group: argparse._ActionsContainer
        if self.is_mutually_exclusive:
            group = parser.add_mutually_exclusive_group()
        else:
            group = parser.add_argument_group()

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
