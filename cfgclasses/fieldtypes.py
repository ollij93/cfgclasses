"""Field types module providing helper functions for defining fields."""
import dataclasses
from typing import Any, Optional, Union

from .argspec import CFG_METADATA_FIELD, ConfigOpts

__all__ = (
    "choices",
    "mutually_exclusive_group",
    "optional",
    "positional",
    "simple",
    "store_true",
)


def _field(
    opts: ConfigOpts,
    **kwargs: Any,
) -> Any:
    return dataclasses.field(
        metadata={CFG_METADATA_FIELD: opts},
        **kwargs,
    )


def simple(
    helpstr: str,
    *,
    default: Any = dataclasses.MISSING,
    default_factory: Any = dataclasses.MISSING,
    optnames: Optional[list[str]] = None,
) -> Any:
    """Setup a simple field with a help string and optionally a default value."""
    return _field(
        ConfigOpts(helpstr, optnamesorpos=(optnames or False)),
        default=default,
        default_factory=default_factory,
    )


def store_true(
    helpstr: str,
    *,
    optnames: Optional[list[str]] = None,
) -> Any:
    """Setup a boolean field that doesn't take a value such a '--debug'."""
    return _field(
        ConfigOpts(helpstr, optnamesorpos=(optnames or False)),
        default=False,
    )


def optional(
    helpstr: str,
    *,
    optnames: Optional[list[str]] = None,
) -> Any:
    """Setup an optional field which defaults to None."""
    return _field(
        ConfigOpts(helpstr, optnamesorpos=(optnames or False)),
        default=None,
    )


def choices(
    helpstr: str,
    choices_: list[Any],
    *,
    default: Any = dataclasses.MISSING,
    default_factory: Any = dataclasses.MISSING,
    optnames: Optional[list[str]] = None,
) -> Any:
    """Setup a choices field with an optional default choice."""
    return _field(
        ConfigOpts(
            helpstr, optnamesorpos=(optnames or False), choices=choices_
        ),
        default=default,
        default_factory=default_factory,
    )


def positional(
    helpstr: str,
    *,
    default: Any = dataclasses.MISSING,
    default_factory: Any = dataclasses.MISSING,
    nargs: Union[int, str, None] = None,
) -> Any:
    """Setup a simple field with a help string and optionally a default value."""
    return _field(
        ConfigOpts(helpstr, optnamesorpos=True, nargs=nargs),
        default=default,
        default_factory=default_factory,
    )


# ==============================================================================
# Utilities for specifiying subgroups
# ==============================================================================


def mutually_exclusive_group() -> Any:
    """Setup a mutually exclusive group."""
    return dataclasses.field(metadata={"mutually_exclusive": True})
