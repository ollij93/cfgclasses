"""Primary module of the cfgclasses package."""
import argparse
import dataclasses
from typing import Generic, Optional, Sequence, Type, TypeVar

from .argspec import Specification
from .configgroup import ConfigGroup, validate_post_argparse

__all__ = (
    "ConfigClass",
    "ConfigSubmode",
)

_T = TypeVar("_T", bound="ConfigClass")
_U = TypeVar("_U", bound="ConfigClass")


@dataclasses.dataclass
class ConfigSubmode(Generic[_T]):
    """Data container for a submode definition."""

    name: str
    configcls: Type[_T]


@dataclasses.dataclass
class ConfigClass(ConfigGroup):
    """Base class to build cfgclasses from."""

    @classmethod
    def parse_args(
        cls: Type[_T], argv: Sequence[str], prog: Optional[str] = None
    ) -> _T:
        """Abstract parse_args method."""
        parser = argparse.ArgumentParser(prog=prog)
        specification = Specification.from_class(cls)
        specification.add_to_parser(parser)
        namespace = parser.parse_args(argv)
        ret = specification.construct_from_namespace(namespace)
        validate_post_argparse(ret, parser)
        return ret

    @classmethod
    def _add_submode_parsers(
        cls, parser: argparse.ArgumentParser, submodes: list[ConfigSubmode[_T]]
    ) -> dict[str, Specification[_T]]:
        """Add the submode parsers to the given argparse parser."""
        submode_specs = {}
        subparsers = parser.add_subparsers()
        for submode in submodes:
            subparser = subparsers.add_parser(
                submode.name, help=submode.configcls.__doc__
            )
            subparser.set_defaults(submode_name=submode.name)
            subspec = Specification.from_class(submode.configcls)
            subspec.add_to_parser(subparser)
            submode_specs[submode.name] = subspec
        return submode_specs

    @classmethod
    def parse_args_with_submodes(
        cls: Type[_T],
        argv: Sequence[str],
        submodes: list[ConfigSubmode[_U]],
        prog: Optional[str] = None,
    ) -> tuple[_T, _U]:
        """Method used to define and process a config class."""
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
