"""Field types module providing helper functions for defining fields."""
import dataclasses
from typing import Any, Iterable, Optional, Union

__all__ = (
    "choices",
    "mutually_exclusive_group",
    "optional",
    "positional",
    "simple",
    "store_true",
)


def _field(
    helpstr: str,
    metadata: Optional[dict[str, Any]] = None,
    *,
    optnames: Optional[Iterable[str]] = None,
    **kwargs: Any,
) -> Any:
    if metadata is None:
        metadata = {}
    if optnames is not None:
        metadata["optnames"] = optnames

    return dataclasses.field(
        metadata=(metadata | {"help": helpstr}),
        **kwargs,
    )


def simple(
    helpstr: str,
    *,
    default: Any = dataclasses.MISSING,
    default_factory: Any = dataclasses.MISSING,
    optnames: Optional[Iterable[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Any:
    """Setup a simple field with a help string and optionally a default value."""
    return _field(
        helpstr,
        metadata,
        default=default,
        default_factory=default_factory,
        optnames=optnames,
    )


def store_true(
    helpstr: str,
    *,
    optnames: Optional[Iterable[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Any:
    """Setup a boolean field that doesn't take a value such a '--debug'."""
    return _field(helpstr, metadata, default=False, optnames=optnames)


def optional(
    helpstr: str,
    *,
    optnames: Optional[Iterable[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Any:
    """Setup an optional field which defaults to None."""
    return _field(helpstr, metadata, default=None, optnames=optnames)


def choices(
    helpstr: str,
    choices_: Iterable[Any],
    *,
    default: Any = dataclasses.MISSING,
    default_factory: Any = dataclasses.MISSING,
    optnames: Optional[Iterable[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Any:
    """Setup a choices field with an optional default choice."""
    if metadata is None:
        metadata = {}
    return _field(
        helpstr,
        metadata | {"choices": choices_},
        default=default,
        default_factory=default_factory,
        optnames=optnames,
    )


def positional(
    helpstr: str,
    *,
    default: Any = dataclasses.MISSING,
    default_factory: Any = dataclasses.MISSING,
    nargs: Union[int, str, None] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Any:
    """Setup a simple field with a help string and optionally a default value."""
    if metadata is None:
        metadata = {}
    if nargs is not None:
        metadata["nargs"] = nargs
    return _field(
        helpstr,
        metadata | {"positional": True},
        default=default,
        default_factory=default_factory,
    )


# ==============================================================================
# Utilities for specifiying subgroups
# ==============================================================================


def mutually_exclusive_group() -> Any:
    """Setup a mutually exclusive group."""
    return dataclasses.field(metadata={"mutually_exclusive": True})
