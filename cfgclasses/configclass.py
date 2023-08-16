"""Primary module of the cfgclasses package."""
import argparse
import dataclasses
from typing import Optional, Sequence, Type, TypeVar

from .argspec import ArgGroup
from .configgroup import ConfigGroup

__all__ = (
    "ConfigClass",
    "ConfigSubmode",
)

_T = TypeVar("_T", bound="ConfigClass")


@dataclasses.dataclass
class ConfigSubmode:
    """Data container for a submode definition."""

    name: str
    configcls: Type["ConfigClass"]


@dataclasses.dataclass
class ConfigClass(ConfigGroup):
    """Base class to build cfgclasses from."""

    @classmethod
    def parse_args(
        cls: Type[_T], argv: Sequence[str], prog: Optional[str] = None
    ) -> _T:
        """Abstract parse_args method."""
        parser = argparse.ArgumentParser(prog=prog)
        arggroup = ArgGroup.from_class(cls)
        arggroup.add_to_parser(parser)
        namespace = parser.parse_args(argv)
        return cls(**arggroup.extract_args_from_namespace(namespace))

    @classmethod
    def parse_args_with_submodes(
        cls: Type[_T],
        argv: Sequence[str],
        submodes: list[ConfigSubmode],
        prog: Optional[str] = None,
    ) -> tuple[_T, "ConfigClass"]:
        """Method used to define and process a config class."""
        if not submodes:
            raise ValueError("Can't parse_args_with_submodes with no submodes")

        parser = argparse.ArgumentParser(prog=prog)
        arggroup = ArgGroup.from_class(cls)
        arggroup.add_to_parser(parser)

        submode_groups = {}
        subparsers = parser.add_subparsers()
        for submode in submodes:
            subparser = subparsers.add_parser(
                submode.name, help=submode.configcls.__doc__
            )
            subparser.set_defaults(submode_name=submode.name)
            subgroup = ArgGroup.from_class(submode.configcls)
            subgroup.add_to_parser(subparser)
            submode_groups[submode.name] = (submode, subgroup)

        namespace = parser.parse_args(argv)
        if submodes and not hasattr(namespace, "submode_name"):
            raise argparse.ArgumentError(None, "No submode selected")

        selected_submode, selected_submode_group = submode_groups[
            namespace.submode_name
        ]
        return (cls(**arggroup.extract_args_from_namespace(namespace))), (
            selected_submode.configcls(
                **selected_submode_group.extract_args_from_namespace(namespace)
            )
        )
