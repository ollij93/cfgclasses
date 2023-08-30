"""Primary module of the cfgclasses package."""
import argparse
import dataclasses
from typing import Optional, Sequence, Type, TypeVar

from .argspec import Specification
from .configgroup import ConfigGroup, validate_post_argparse

__all__ = (
    "ConfigClass",
    "MutuallyExclusiveConfigClass",
)

_T = TypeVar("_T", bound="ConfigClass")
_U = TypeVar("_U", bound="ConfigClass")


@dataclasses.dataclass
class ConfigClass(ConfigGroup):
    """
    Base class to build cfgclasses from.
    """

    @classmethod
    def parse_args(
        cls: Type[_T], argv: Sequence[str], prog: Optional[str] = None
    ) -> _T:
        """
        Parse the arguments vector into an instance of this class.

        :param argv: The arguments vector to parse.
        :param prog: The name of the program to display in the help message.
        :rtype: ``ConfigClass``
        :return: An instance of this class with the parsed arguments.
        """
        parser = argparse.ArgumentParser(prog=prog)
        specification = Specification.from_class(cls)
        specification.add_to_parser(parser)
        namespace = parser.parse_args(argv)
        ret = specification.construct_from_namespace(namespace)
        validate_post_argparse(ret, parser)
        return ret

    @classmethod
    def _add_submode_parsers(
        cls, parser: argparse.ArgumentParser, submodes: dict[str, Type[_T]]
    ) -> dict[str, Specification[_T]]:
        """Add the submode parsers to the given argparse parser."""
        submode_specs = {}
        subparsers = parser.add_subparsers()
        for name, submode in submodes.items():
            subparser = subparsers.add_parser(name, help=submode.__doc__)
            subparser.set_defaults(submode_name=name)
            subspec = Specification.from_class(submode)
            subspec.add_to_parser(subparser)
            submode_specs[name] = subspec
        return submode_specs

    @classmethod
    def parse_args_with_submodes(
        cls: Type[_T],
        argv: Sequence[str],
        submodes: dict[str, Type[_U]],
        prog: Optional[str] = None,
    ) -> tuple[_T, _U]:
        """
        Parse the arguments vector into an instance of this class and a submode.

        The submode will be one of the provided submodes classes populated with
        the CLI arguments.

        :param argv: The arguments vector to parse.
        :param submodes: Mapping of submode name to submode classes to parse.
        :param prog: The name of the program to display in the help message.
        :rtype: ``tuple[ConfigClass, ConfigClass]``
        :return: A tuple of the top-level config and the submode config.
        :raises ValueError: If no submodes are provided.
        """
        if not submodes:
            raise ValueError("Can't parse_args_with_submodes with no submodes")

        parser = argparse.ArgumentParser(prog=prog)
        spec = Specification.from_class(cls)
        spec.add_to_parser(parser)

        submode_specs = cls._add_submode_parsers(parser, submodes)

        namespace = parser.parse_args(argv)
        if submodes and not hasattr(namespace, "submode_name"):
            parser.error("No submode selected")

        selected_submode_spec = submode_specs[namespace.submode_name]
        toplvlcfg = spec.construct_from_namespace(namespace)
        submodecfg = selected_submode_spec.construct_from_namespace(namespace)
        validate_post_argparse(toplvlcfg, parser)
        validate_post_argparse(submodecfg, parser)
        return toplvlcfg, submodecfg


class MutuallyExclusiveConfigClass(ConfigClass):
    """Sub-class to build mutually exclusive cfgclasses from."""

    @classmethod
    def add_argument_group(
        cls, parser: argparse._ActionsContainer
    ) -> argparse._ActionsContainer:
        """
        Override add_argument_group to add a mutually exclusive group.

        :meta private:
        """
        return parser.add_mutually_exclusive_group()
