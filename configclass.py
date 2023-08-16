"""Primary module of the configclasses package."""
import argparse
import dataclasses
from pathlib import Path
from typing import Any, Optional, Sequence, Type, TypeVar

import yaml

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

    def add_subparser(
        self, subparsers: "argparse._SubParsersAction[Any]"
    ) -> ArgGroup:
        """Add this submode to the given parser."""
        subparser = subparsers.add_parser(
            self.name, help=self.configcls.__doc__
        )
        subparser.set_defaults(submode_name=self.name)
        subgroup = ArgGroup.from_class(self.configcls)
        subgroup.add_to_parser(subparser)
        return subgroup


@dataclasses.dataclass
class ConfigClass(ConfigGroup):
    """Base class to build configclasses from."""

    @classmethod
    def _construct_parser(
        cls, prog: Optional[str], submodes: list[ConfigSubmode]
    ) -> tuple[
        argparse.ArgumentParser,
        ArgGroup,
        dict[str, tuple[ConfigSubmode, ArgGroup]],
    ]:
        """Construct the parser for this configclass."""
        parser = argparse.ArgumentParser(prog=prog)
        arggroup = ArgGroup.from_class(cls)
        arggroup.add_to_parser(parser)

        submode_groups = {}
        subparsers = parser.add_subparsers()
        for submode in submodes:
            submode_groups[submode.name] = (
                submode,
                submode.add_subparser(subparsers),
            )

        return parser, arggroup, submode_groups

    @staticmethod
    def _get_userconfig(
        useryamlconfig: Optional[Path],
        *,
        submode_name: Optional[str] = None,
    ) -> tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
        """Get the user config from the given path."""
        userconfig = (
            yaml.safe_load(useryamlconfig.read_text())
            if useryamlconfig
            else None
        )
        return userconfig, (
            userconfig.get(f"submode.{submode_name}")
            if userconfig is not None
            else None
        )

    @classmethod
    def parse_args(
        cls: Type[_T],
        argv: Sequence[str],
        prog: Optional[str] = None,
        *,
        useryamlconfig: Optional[Path] = None,
    ) -> _T:
        """Abstract parse_args method."""
        # Construct the parser
        parser, arggroup, _ = cls._construct_parser(prog, [])

        # Parse the arguments
        namespace = parser.parse_args(argv)

        # Handle other configuration sources
        userconfig, _ = cls._get_userconfig(useryamlconfig)

        # Construct the resulting class instance
        return arggroup.to_configclass(cls, namespace, userconfig=userconfig)

    @classmethod
    def parse_args_with_submodes(
        cls: Type[_T],
        argv: Sequence[str],
        submodes: list[ConfigSubmode],
        prog: Optional[str] = None,
        *,
        useryamlconfig: Optional[Path] = None,
    ) -> tuple[_T, "ConfigClass"]:
        """Method used to define and process a config class."""
        if not submodes:
            raise ValueError("Can't parse_args_with_submodes with no submodes")

        # Construct the parser
        parser, arggroup, submode_groups = cls._construct_parser(
            prog, submodes
        )

        # Parse the arguments
        namespace = parser.parse_args(argv)

        # Confirm the submode selection
        if submodes and not hasattr(namespace, "submode_name"):
            raise argparse.ArgumentError(None, "No submode selected")

        selected_submode, selected_submode_group = submode_groups[
            namespace.submode_name
        ]

        # Handle other configuration sources
        userconfig, submodeuserconfig = cls._get_userconfig(
            useryamlconfig, submode_name=namespace.submode_name
        )

        # Construct the resulting class instances
        toplvlconfig = arggroup.to_configclass(
            cls, namespace, userconfig=userconfig
        )
        return toplvlconfig, (
            selected_submode_group.to_configclass(
                selected_submode.configcls,
                namespace,
                userconfig=submodeuserconfig,
            )
        )
