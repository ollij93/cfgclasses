"""Module defining the arg() function for creating dataclass fields."""
import dataclasses
from typing import Any, Callable, Optional, Type, TypeVar, overload

from .argspec import (
    CFG_METADATA_FIELD,
    ConfigClassTransform,
    ConfigOpts,
    NonPositionalConfigOpts,
)
from .configclass import ConfigClass

__all__ = (
    "arg",
    "cfgtransform",
    "optional",
)

_T = TypeVar("_T")
_U = TypeVar("_U")
_ConfigClassT = TypeVar("_ConfigClassT", bound=ConfigClass)


@overload
def arg(
    helpstr: str,
    *optnames: str,
    metavar: Optional[str] = ...,
    choices: Optional[list[_T]] = ...,
) -> _T:
    """Non-positional overload with no default."""


@overload
def arg(
    helpstr: str,
    *optnames: str,
    default_factory: Callable[[], _T],
    metavar: Optional[str] = ...,
    choices: Optional[list[_T]] = ...,
) -> _T:
    """Non-positional overload with a default."""


@overload
def arg(
    helpstr: str,
    *optnames: str,
    default: _T,
    metavar: Optional[str] = ...,
    choices: Optional[list[_T]] = ...,
) -> _T:
    """Non-positional overload with a default_factory."""


@overload
def arg(
    helpstr: str,
    *,
    positional: bool,
    metavar: Optional[str] = ...,
    choices: Optional[list[_T]] = ...,
) -> _T:
    """Positional overload with no default."""


@overload
def arg(
    helpstr: str,
    *,
    positional: bool,
    default_factory: Callable[[], _T],
    metavar: Optional[str] = ...,
    choices: Optional[list[_T]] = ...,
) -> _T:
    """Positional overload with a default."""


@overload
def arg(
    helpstr: str,
    *,
    positional: bool,
    default: _T,
    metavar: Optional[str] = ...,
    choices: Optional[list[_T]] = ...,
) -> _T:
    """Positional overload with a default_factory."""


@overload
def arg(
    helpstr: str,
    *optnames: str,
    metavar: Optional[str] = ...,
    choices: Optional[list[_U]] = ...,
    transform: Callable[[_U], _T],
    transform_type: Type[_U],
) -> _T:
    """Non-positional overload with no default and a transform function."""


@overload
def arg(
    helpstr: str,
    *optnames: str,
    default_factory: Callable[[], _U],
    metavar: Optional[str] = ...,
    choices: Optional[list[_U]] = ...,
    transform: Callable[[_U], _T],
    transform_type: Type[_U],
) -> _T:
    """Non-positional overload with a default and a transform function."""


@overload
def arg(
    helpstr: str,
    *optnames: str,
    default: _U,
    metavar: Optional[str] = ...,
    choices: Optional[list[_U]] = ...,
    transform: Callable[[_U], _T],
    transform_type: Type[_U],
) -> _T:
    """Non-positional overload with a default_factory and a transform function."""


@overload
def arg(
    helpstr: str,
    *,
    positional: bool,
    metavar: Optional[str] = ...,
    choices: Optional[list[_U]] = ...,
    transform: Callable[[_U], _T],
    transform_type: Type[_U],
) -> _T:
    """Positional overload with no default and a transform function."""


@overload
def arg(
    helpstr: str,
    *,
    positional: bool,
    default_factory: Callable[[], _U],
    metavar: Optional[str] = ...,
    choices: Optional[list[_U]] = ...,
    transform: Callable[[_U], _T],
    transform_type: Type[_U],
) -> _T:
    """Positional overload with a default and a transform function."""


@overload
def arg(
    helpstr: str,
    *,
    positional: bool,
    default: _U,
    metavar: Optional[str] = ...,
    choices: Optional[list[_U]] = ...,
    transform: Callable[[_U], _T],
    transform_type: Type[_U],
) -> _T:
    """Positional overload with a default_factory and a transform function."""


def arg(
    helpstr: str,
    *optnames: str,
    positional: bool = False,
    metavar: Optional[str] = None,
    choices: Optional[list[Any]] = None,
    default: Any = dataclasses.MISSING,
    default_factory: Any = dataclasses.MISSING,
    transform: Optional[Callable[[Any], Any]] = None,
    transform_type: Optional[Type[Any]] = None,
) -> Any:
    """
    Create a dataclass field with additional cfgclasses options stored.

    :param helpstr: Help string for this fields argument.
    :param optnames: Optional list of option names for this fields argument.
        E.g. ``["-v", "--verbose"]``.
    :param positional: If true, use a positional argument for this field. Cannot
        be used with ``optnames``.
    :param metavar: Metavar to display alongside the argument for the field.
    :param choices: List of valid choices for the value of this field.
    :param default: Default value for the field if not given on the CLI.
    :param default_factory: Default factory to construct an instance of the
        field if not given on the CLI.
    :param transform: Function to transform the value of the field after parsing
        from the CLI.
    :param transform_type: Input type for the transform function. I.e. the type
        read from the CLI.
    :return: The resulting dataclass field.
    """
    cli_default = default
    if (
        cli_default is dataclasses.MISSING
        and default_factory is not dataclasses.MISSING
    ):
        cli_default = default_factory()

    # Typing of transforms here's is very Any-like, but the overloads for this
    # function are used to specify the typing for the public API so nothing
    # stronger is needed here.
    # There's no need to do anything stronger internally since we're putting the
    # ConfigOpts into the dataclasses metadata which has no typing associated
    # with it anyway.
    if positional:
        opts = ConfigOpts(
            help=helpstr,
            metavar=metavar,
            choices=choices,
            transform=transform,
            transform_type=transform_type,
            default=cli_default,
        )
    else:
        opts = NonPositionalConfigOpts(
            help=helpstr,
            metavar=metavar,
            choices=choices,
            transform=transform,
            transform_type=transform_type,
            default=cli_default,
            optnames=list(optnames),
        )

    if default is not dataclasses.MISSING:
        return dataclasses.field(
            default=transform(default) if transform else default,
            metadata={CFG_METADATA_FIELD: opts},
        )
    if default_factory is not dataclasses.MISSING:
        return dataclasses.field(
            default_factory=(
                (lambda: transform(default_factory()))
                if transform
                else default_factory
            ),
            metadata={CFG_METADATA_FIELD: opts},
        )
    return dataclasses.field(
        metadata={CFG_METADATA_FIELD: opts},
    )


@overload
def optional(
    helpstr: str,
    *optnames: str,
    metavar: Optional[str] = ...,
    choices: Optional[list[_T]] = ...,
) -> _T:
    """Positional overload."""


@overload
def optional(
    helpstr: str,
    *,
    positional: bool = ...,
    metavar: Optional[str] = ...,
    choices: Optional[list[_T]] = ...,
) -> _T:
    """Non-positional overload."""


@overload
def optional(
    helpstr: str,
    *optnames: str,
    metavar: Optional[str] = ...,
    choices: Optional[list[_U]] = ...,
    transform: Callable[[_U], _T],
    transform_type: Type[_U],
) -> _T:
    """Positional overload with a transform function."""


@overload
def optional(
    helpstr: str,
    *,
    positional: bool = ...,
    metavar: Optional[str] = ...,
    choices: Optional[list[_U]] = ...,
    transform: Callable[[_U], _T],
    transform_type: Type[_U],
) -> _T:
    """Non-positional overload with a transform function."""


def optional(
    helpstr: str,
    *optnames: str,
    positional: bool = False,
    metavar: Optional[str] = None,
    choices: Optional[list[Any]] = None,
    transform: Optional[Callable[[Any], Any]] = None,
    transform_type: Optional[Type[Any]] = None,
) -> Any:
    """
    Create a field with cfgclasses options with a default of None.

    :param helpstr: Help string for this fields argument.
    :param optnames: Optional list of option names for this fields argument.
        E.g. ``["-v", "--verbose"]``.
    :param positional: If true, use a positional argument for this field. Cannot
        be used with ``optnames``.
    :param metavar: Metavar to display alongside the argument for the field.
    :param choices: List of valid choices for the value of this field.
    :param transform: Function to transform the value of the field after parsing
        from the CLI.
    :param transform_type: Input type for the transform function. I.e. the type
        read from the CLI.
    :return: The resulting dataclass field.
    """
    if transform and transform_type:
        ret = arg(
            helpstr,
            *optnames,
            positional=positional,
            metavar=metavar,
            choices=choices,
            default=None,
            transform=transform,
            transform_type=transform_type,
        )
    else:
        ret = arg(
            helpstr,
            *optnames,
            positional=positional,
            metavar=metavar,
            choices=choices,
            default=None,
        )
    return ret


def cfgtransform(
    transform_type: Type[_ConfigClassT],
    transform: Callable[[_ConfigClassT], _U],
) -> _U:
    """
    Create a field for a nested ConfigClass with a transform.

    :param transform_type: The type that the transform function takes as input.
    :param transform: The transform function to apply.
    :return: The resulting dataclass field.
    """
    ret: _U = dataclasses.field(
        metadata={
            CFG_METADATA_FIELD: ConfigClassTransform(transform, transform_type)
        }
    )
    return ret
