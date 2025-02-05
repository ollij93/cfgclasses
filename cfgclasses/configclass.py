"""Primary module of the cfgclasses package."""

import argparse
import dataclasses
from typing import Optional, Sequence, Type, TypeVar

from .argspec import CFG_MUTUALLY_EXCLUSIVE_ATTR, Specification
from .validation import validate_post_argparse, validator

# typeshed not available at runtime, only for type checking
try:
    from _typeshed import DataclassInstance
except ImportError:
    DataclassInstance = None  # type: ignore

_T = TypeVar("_T", bound=DataclassInstance)
_U = TypeVar("_U")

__all__ = (
    "ConfigClass",
    "MutuallyExclusiveConfigClass",
    "parse_args",
    "parse_known_args",
    "parse_args_with_submodes",
    "parse_known_args_with_submodes",
    "mutually_exclusive",
)


def parse_args(
    cls: Type[_T],
    argv: Sequence[str],
    prog: Optional[str] = None,
) -> _T:
    """
    Parse the arguments vector into an instance of the given class.

    :param cls: The class to parse the arguments into.
    :param argv: The arguments vector to parse.
    :param prog: The name of the program to display in the help message.
    :rtype: ``cls``
    :return: An instance of the given class with the parsed arguments.
    """
    parser = argparse.ArgumentParser(prog=prog)
    specification = Specification.from_class(cls)
    specification.add_to_parser(parser)
    namespace = parser.parse_args(argv)
    ret = specification.construct_from_namespace(namespace)
    validate_post_argparse(ret, parser)
    return ret


def parse_known_args(
    cls: Type[_T],
    argv: Sequence[str],
    prog: Optional[str] = None,
) -> tuple[_T, list[str]]:
    """
    Parse the known arguments from the input vector into an instance of the given class.

    :param cls: The class to parse the arguments into.
    :param argv: The arguments vector to parse.
    :param prog: The name of the program to display in the help message.
    :rtype: ``tuple[cls, list[str]]``
    :return:
        An instance of the given class with the parsed arguments, plus a
        list of unknown arguments.
    """
    parser = argparse.ArgumentParser(prog=prog)
    specification = Specification.from_class(cls)
    specification.add_to_parser(parser)
    namespace, unknown_args = parser.parse_known_args(argv)
    ret = specification.construct_from_namespace(namespace)
    validate_post_argparse(ret, parser)
    return ret, unknown_args


def _add_submode_parsers(
    parser: argparse.ArgumentParser,
    submodes: dict[str, Type[_T]],
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

    :param cls: The class to parse the arguments into.
    :param argv: The arguments vector to parse.
    :param submodes: Mapping of submode name to submode classes to parse.
    :param prog: The name of the program to display in the help message.
    :rtype: ``tuple[cls, submode]``
    :return: A tuple of the top-level config and the submode config.
    :raises ValueError: If no submodes are provided.
    """
    if not submodes:
        raise ValueError("Can't parse_args_with_submodes with no submodes")

    parser = argparse.ArgumentParser(prog=prog)
    spec = Specification.from_class(cls)
    spec.add_to_parser(parser)

    # mypy doesn't track the dataclass-ness of the submodes dict values properly
    # so sanity check here and then cast to the correct type (mypy ignore)
    for submode in submodes.values():
        if not dataclasses.is_dataclass(submode):
            raise TypeError(f"{submode} is not a dataclass")
    submode_specs = _add_submode_parsers(parser, submodes)  # type:ignore

    namespace = parser.parse_args(argv)
    if submodes and not hasattr(namespace, "submode_name"):
        parser.error("No submode selected")

    selected_submode_spec = submode_specs[namespace.submode_name]
    toplvlcfg = spec.construct_from_namespace(namespace)
    submodecfg = selected_submode_spec.construct_from_namespace(namespace)
    validate_post_argparse(toplvlcfg, parser)
    validate_post_argparse(submodecfg, parser)
    return toplvlcfg, submodecfg


def parse_known_args_with_submodes(
    cls: Type[_T],
    argv: Sequence[str],
    submodes: dict[str, Type[_U]],
    prog: Optional[str] = None,
) -> tuple[_T, _U, list[str]]:
    """
    Parse the known arguments from the input vector into an instance of this class and a submode.

    The submode will be one of the provided submodes classes populated with
    the CLI arguments.

    :param cls: The class to parse the arguments into.
    :param argv: The arguments vector to parse.
    :param submodes: Mapping of submode name to submode classes to parse.
    :param prog: The name of the program to display in the help message.
    :rtype: ``tuple[cls, submode, list[str]]``
    :return:
        A tuple of the top-level config, the submode config and a list of
        unknown arguments.
    :raises ValueError: If no submodes are provided.
    """
    if not submodes:
        raise ValueError("Can't parse_args_with_submodes with no submodes")

    parser = argparse.ArgumentParser(prog=prog)
    spec = Specification.from_class(cls)
    spec.add_to_parser(parser)

    # mypy doesn't track the dataclass-ness of the submodes dict values properly
    # so sanity check here and then cast to the correct type (mypy ignore)
    for submode in submodes.values():
        if not dataclasses.is_dataclass(submode):
            raise TypeError(f"{submode} is not a dataclass")
    submode_specs = _add_submode_parsers(parser, submodes)  # type:ignore

    namespace, unknown_args = parser.parse_known_args(argv)
    if submodes and not hasattr(namespace, "submode_name"):
        parser.error("No submode selected")

    selected_submode_spec = submode_specs[namespace.submode_name]
    toplvlcfg = spec.construct_from_namespace(namespace)
    submodecfg = selected_submode_spec.construct_from_namespace(namespace)
    validate_post_argparse(toplvlcfg, parser)
    validate_post_argparse(submodecfg, parser)
    return toplvlcfg, submodecfg, unknown_args


@dataclasses.dataclass
class ConfigClass:
    """
    Base class to build cfgclasses from.

    .. deprecated:: 2.2.0
        Use the :func:`cfgclasses.parse_args` or
        `cfgclasses.parse_args_with_submodes` functions instead.
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
        return parse_args(cls, argv, prog)

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
        return parse_args_with_submodes(cls, argv, submodes, prog)

    # Register the validate() method as a validator for subclasses to keep
    # consistent API with old versions.
    @validator
    def _cfgclass_default_validator(self) -> None:
        """Validate the config class instance raising a ValueError if invalid."""
        if hasattr(self, "validate"):
            self.validate()


def mutually_exclusive(cls: Type[_T]) -> Type[_T]:
    """
    Decorator to mark a class as representing a mutually exclusive group.

    :param cls: The class to mark as mutually exclusive.
    :return: The modified input class.
    """
    setattr(cls, CFG_MUTUALLY_EXCLUSIVE_ATTR, True)
    return cls


@mutually_exclusive
class MutuallyExclusiveConfigClass(ConfigClass):
    """
    Sub-class to build mutually exclusive cfgclasses from.

    .. deprecated:: 2.2.0
        Use the `@cfgclasses.mutually_exclusive` class decorator instead.
    """
