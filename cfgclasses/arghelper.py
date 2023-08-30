"""Module defining the arg() function for creating dataclass fields."""
import dataclasses
from typing import Any, Callable, Optional, TypeVar, overload

from .argspec import CFG_METADATA_FIELD, ConfigOpts, NonPositionalConfigOpts

__all__ = (
    "arg",
    "optional",
)

_T = TypeVar("_T")


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


def arg(
    helpstr: str,
    *optnames: str,
    positional: bool = False,
    metavar: Optional[str] = None,
    choices: Optional[list[Any]] = None,
    default: Any = dataclasses.MISSING,
    default_factory: Any = dataclasses.MISSING,
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
    :return: The resulting dataclass field.
    """
    if positional:
        opts = ConfigOpts(helpstr, metavar, choices)
    else:
        opts = NonPositionalConfigOpts(
            helpstr, metavar, choices, list(optnames)
        )

    if default is not dataclasses.MISSING:
        return dataclasses.field(
            default=default,
            metadata={CFG_METADATA_FIELD: opts},
        )
    if default_factory is not dataclasses.MISSING:
        return dataclasses.field(
            default_factory=default_factory,
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


def optional(
    helpstr: str,
    *optnames: str,
    positional: bool = False,
    metavar: Optional[str] = None,
    choices: Optional[list[Any]] = None,
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
    :return: The resulting dataclass field.
    """
    return arg(
        helpstr,
        *optnames,
        positional=positional,
        metavar=metavar,
        choices=choices,
        default=None,
    )
