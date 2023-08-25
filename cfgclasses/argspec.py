"""Module for defining the argument specification for a ConfigClass."""
import argparse
import dataclasses
from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
)

from .configgroup import ConfigGroup


class ArgSpecNotSpecified:
    """Type for unspecified argument specifiers"""

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ArgSpecNotSpecified)


def _argspec_optional() -> Any:
    return dataclasses.field(default_factory=ArgSpecNotSpecified)


def argparse_type_from_field(field: dataclasses.Field[Any]) -> Type[Any]:
    """Get the type to use for a field when interacting with argparse."""
    return field.metadata.get("transform_from") or field.type


@dataclasses.dataclass
class ArgOpts:
    """
    Options for an argument to be passed to
    argparse.ArgumentParser.add_argument().

    ..attribute:: default
        Default value for the argument.
    ..attribute:: required
        Whether the argument is required.
    ..attribute:: metavar
        Name to display for the argument in usage messages.
    ..attribute:: choices
        List of valid choices for the argument.
    ..attribute:: action
        Action to take when the argument is encountered. E.g. "store_true"
    ..attribute:: type
        Type of the argument. E.g. int, str, etc.
    """

    default: Any = _argspec_optional()
    required: bool | ArgSpecNotSpecified = _argspec_optional()
    metavar: str | ArgSpecNotSpecified = _argspec_optional()
    choices: Iterable[Any] | ArgSpecNotSpecified = _argspec_optional()
    action: str | ArgSpecNotSpecified = _argspec_optional()
    type: Type[Any] | ArgSpecNotSpecified = _argspec_optional()
    nargs: Union[int, str] | ArgSpecNotSpecified = _argspec_optional()

    def to_kwargs(self) -> dict[str, Any]:
        """Convert to kwargs for argparse.ArgumentParser.add_argument()"""
        return {
            k: v
            for k, v in dataclasses.asdict(self).items()
            if not isinstance(v, ArgSpecNotSpecified)
        }

    @staticmethod
    def from_field(
        type_: Type[Any], field: dataclasses.Field[Any]
    ) -> "ArgOpts":
        """Instantiate an instance of this class from the field definition."""
        opts = ArgOpts()
        # For boolean types that do not default to true, use the 'store_true' action
        # allowing flags like `--debug` to be used rather than `--debug True`
        if type_ == bool and field.default is not True:
            opts.action = "store_true"
        # Handle list types specially using nargs
        elif get_origin(type_) == list:
            opts.nargs = "+"
            opts.type = get_args(type_)[0]
        # Handle special Union types - see individual details
        elif get_origin(type_) == Union:
            type_args = get_args(type_)
            # For `Optional[type]` just set required=False and specify the type
            if len(type_args) == 2 and type(None) in type_args:
                opts.type = [a for a in type_args if a is not None][0]
                opts.required = False
            # No other Union types are currently supported
            else:
                raise TypeError(f"Can't handle Union of types: {type_args}")
        # For all remaining types, just leave the type for argparse to deal with
        else:
            opts.type = type_

        if field.default is not dataclasses.MISSING:
            opts.default = field.default
        elif field.default_factory is not dataclasses.MISSING:
            opts.default = field.default_factory()
        else:
            opts.required = True

        opts.metavar = field.metadata.get("metavar", ArgSpecNotSpecified())
        opts.choices = field.metadata.get("choices", ArgSpecNotSpecified())
        # Allow users to override nargs, e.g. to go from "+" -> "*" if empty
        # lists are permitted
        if opts.nargs != ArgSpecNotSpecified():
            opts.nargs = field.metadata.get("nargs", opts.nargs)
        elif "nargs" in field.metadata:
            raise TypeError(f"Can't override nargs for non-list type {type_}")

        return opts


@dataclasses.dataclass
class ArgSpec:
    """
    Specification for a single argument to be passed to
    argparse.ArgumentParser.add_argument().

    ..attribute:: name
        Name of the argument used as "--name" on the command line.
    ..attribute:: help
        Help string for the argument.
    ..attribute:: optnames
        List of names (such as -f or --foo) for the argument.
    ..attribute:: opts
        ArgOpts instance containing the options for the argument.
    ..attribute:: transform
        Function to transform the value of the argument.
    """

    name: str
    help: str
    optnames: list[str]
    opts: ArgOpts = dataclasses.field(default_factory=ArgOpts)
    transform: Optional[Callable[[Any], Any]] = dataclasses.field(default=None)

    @staticmethod
    def from_field(field: dataclasses.Field[Any]) -> "ArgSpec":
        """Instantiate an instance of this class from the field definition."""
        type_ = argparse_type_from_field(field)
        opts = ArgOpts.from_field(type_, field)
        positional = field.metadata.get("positional", False)
        if positional:
            # For positional arguments, its not valid to pass the required flag
            opts.required = ArgSpecNotSpecified()

        name = field.name.replace("_", "-")
        optnames = list(
            (field.metadata.get("optnames") or [f"--{name}"])
            if not positional
            else [name]
        )
        return ArgSpec(
            name,
            field.metadata.get("help", ""),
            optnames,
            opts,
            field.metadata.get("transform"),
        )

    def add_to_parser(self, parser: argparse._ActionsContainer) -> None:
        """Add this argument to the given parser."""
        kwargs: dict[str, Any] = {}
        if self.optnames != [self.name]:
            kwargs["dest"] = self.name
        parser.add_argument(
            *self.optnames,
            help=self.help,
            **(kwargs | self.opts.to_kwargs()),
        )

    def from_namespace(self, namespace: argparse.Namespace) -> Any:
        """Extract the value of this argument from an argparse.Namespace."""
        transform = self.transform or (lambda x: x)
        return transform(getattr(namespace, self.name))


@dataclasses.dataclass
class ArgSubGroup:
    """
    Container for a subgroup in an argument group.

    ..attribute:: name
        Name of the subgroup.
    ..attribute:: type
        ConfigClass type of the subgroup.
    ..attribute:: group
        The ArgGroup for the subgroup.
    ..attribute:: transform
        Function to transform the value of the subgroup.
    """

    name: str
    type: Type[ConfigGroup]
    group: "ArgGroup"
    transform: Optional[Callable[[Any], Any]] = dataclasses.field(default=None)

    def from_namespace(self, namespace: argparse.Namespace) -> Any:
        """Extract the value of this subgroup from an argparse.Namespace."""
        transform = self.transform or (lambda x: x)
        return transform(
            self.type(**self.group.extract_args_from_namespace(namespace))
        )


@dataclasses.dataclass
class ArgGroup:
    """Specification for a group of arguments to be passed to
    argparse.ArgumentParser.add_argument_group() or
    argparse.ArgumentParser.add_mutually_exclusive_group().

    ..attribute:: is_mutually_exclusive
        Whether this group is mutually exclusive.
    ..attribute:: members
        List of ArgSpecs for the members of this group.
    ..attribute:: subgroups
        Mapping of group names to ArgGroup for any subgroups of this group.
    """

    is_mutually_exclusive: bool = dataclasses.field(default=False)
    members: list[ArgSpec] = dataclasses.field(default_factory=list)
    subgroups: list[ArgSubGroup] = dataclasses.field(default_factory=list)

    @staticmethod
    def from_class(
        configcls: Type[ConfigGroup], is_mutually_exclusive: bool = False
    ) -> "ArgGroup":
        """Instantiate an instance of this class from the ConfigGroup class"""
        group = ArgGroup(is_mutually_exclusive=is_mutually_exclusive)
        for field in dataclasses.fields(configcls):
            type_ = argparse_type_from_field(field)
            try:
                isconfigcls = issubclass(type_, ConfigGroup)
            except TypeError:
                isconfigcls = False

            if isconfigcls:
                group.subgroups.append(
                    ArgSubGroup(
                        field.name,
                        type_,
                        ArgGroup.from_class(
                            type_,
                            field.metadata.get("mutually_exclusive", False),
                        ),
                        field.metadata.get("transform"),
                    )
                )
            else:
                group.members.append(ArgSpec.from_field(field))
        return group

    def add_to_parser(self, parser: argparse._ActionsContainer) -> None:
        """Add this argument group to the given parser."""
        group: argparse._ActionsContainer
        if self.is_mutually_exclusive:
            group = parser.add_mutually_exclusive_group()
        else:
            group = parser.add_argument_group()

        for member in self.members:
            member.add_to_parser(group)
        for subgroup in self.subgroups:
            subgroup.group.add_to_parser(group)

    def extract_args_from_namespace(
        self, namespace: argparse.Namespace
    ) -> dict[str, Any]:
        """Extract arguments from an argparse.Namespace."""
        return {
            spec.name.replace("-", "_"): spec.from_namespace(namespace)
            for spec in self.members
        } | {
            subgroup.name: subgroup.from_namespace(namespace)
            for subgroup in self.subgroups
        }
