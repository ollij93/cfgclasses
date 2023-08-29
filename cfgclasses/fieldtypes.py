"""Field types module providing helper functions for defining fields."""
import dataclasses
from typing import Any, Optional

from .argspec import CFG_METADATA_FIELD, ConfigOpts, NonPositionalConfigOpts

__all__ = (
    "choices",
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
        NonPositionalConfigOpts(helpstr, optnames=optnames or []),
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
        NonPositionalConfigOpts(helpstr, optnames=optnames or []),
    )


def optional(
    helpstr: str,
    *,
    optnames: Optional[list[str]] = None,
) -> Any:
    """Setup an optional field which defaults to None."""
    return _field(
        NonPositionalConfigOpts(helpstr, optnames=optnames or []),
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
        NonPositionalConfigOpts(
            helpstr, optnames=optnames or [], choices=choices_
        ),
        default=default,
        default_factory=default_factory,
    )


def positional(
    helpstr: str,
    *,
    default: Any = dataclasses.MISSING,
    default_factory: Any = dataclasses.MISSING,
) -> Any:
    """Setup a simple field with a help string and optionally a default value."""
    return _field(
        ConfigOpts(helpstr),
        default=default,
        default_factory=default_factory,
    )
