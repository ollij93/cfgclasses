"""Field types module providing helper functions for defining fields."""
import dataclasses
from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)

__all__ = (
    "arg",
    "choices",
    "mutually_exclusive_group",
    "optional",
    "positional",
    "store_true",
)


_T = TypeVar("_T")
_U = TypeVar("_U")


# ==============================================================================
# Primary entry point for defining the argument field type
#
# Overloads match those for the dataclass.field method allowing either default
# or default_factory to be specified, but not both and providing a valid return
# type.
#
# Additionally the transform arguments can be supplied and the type determined
# from there.
# ==============================================================================


# No defaults, no transform
@overload
def arg(
    helpstr: str,
    *optnames: str,
    metadata: Optional[dict[str, Any]] = ...,
) -> Any:
    pass


# No defaults, with transform
@overload
def arg(
    helpstr: str,
    *optnames: str,
    metadata: Optional[dict[str, Any]] = ...,
    transform: Callable[[_U], _T] = ...,
    transform_from: Type[_U] = ...,
) -> _T:
    pass


# Default, no transform
@overload
def arg(
    helpstr: str,
    *optnames: str,
    default: _T = ...,
    metadata: Optional[dict[str, Any]] = ...,
) -> _T:
    pass


# Default, with transform
@overload
def arg(
    helpstr: str,
    *optnames: str,
    default: _T = ...,
    metadata: Optional[dict[str, Any]] = ...,
    transform: Callable[[_U], _T] = ...,
    transform_from: Type[_U] = ...,
) -> _T:
    pass


# Default factory, no transform
@overload
def arg(
    helpstr: str,
    *optnames: str,
    default_factory: Callable[[], _T] = ...,
    metadata: Optional[dict[str, Any]] = ...,
) -> _T:
    pass


# Default factory, with transform
@overload
def arg(
    helpstr: str,
    *optnames: str,
    default_factory: Callable[[], _T] = ...,
    metadata: Optional[dict[str, Any]] = ...,
    transform: Callable[[_U], _T] = ...,
    transform_from: Type[_U] = ...,
) -> _T:
    pass


def arg(
    helpstr: str,
    *optnames: str,
    default: Any = dataclasses.MISSING,
    default_factory: Any = dataclasses.MISSING,
    metadata: Optional[dict[str, Any]] = None,
    transform: Optional[Callable[[Any], Any]] = None,
    transform_from: Optional[Type[Any]] = None,
) -> Any:
    """Define a dataclass field suitable for use as a cfgclasses cli argument."""
    kwargs = {}
    if default is not dataclasses.MISSING:
        kwargs["default"] = default
    if default_factory is not dataclasses.MISSING:
        kwargs["default_factory"] = default_factory

    metadata = (metadata or {}) | {
        "help": helpstr,
        "optnames": optnames,
        "transform": transform,
        "transform_from": transform_from,
    }
    return dataclasses.field(
        metadata=metadata,
        **kwargs,
    )


# ==============================================================================
# Utilities for common field types
# ==============================================================================
def store_true(
    helpstr: str,
    *optnames: str,
    metadata: Optional[dict[str, Any]] = None,
) -> Any:
    """Setup a boolean field that doesn't take a value such as '--debug'."""
    return arg(helpstr, *optnames, metadata=metadata, default=False)


def optional(
    helpstr: str,
    *optnames: str,
    metadata: Optional[dict[str, Any]] = None,
) -> Any:
    """Setup an optional field which defaults to None."""
    return arg(helpstr, *optnames, metadata=metadata, default=None)


@overload
def choices(
    helpstr: str,
    choices_: Iterable[_T],
    *optnames: str,
    metadata: Optional[dict[str, Any]] = None,
) -> _T:
    pass


@overload
def choices(
    helpstr: str,
    choices_: Iterable[_T],
    *optnames: str,
    default: _T = ...,
    metadata: Optional[dict[str, Any]] = None,
) -> _T:
    pass


def choices(
    helpstr: str,
    choices_: Iterable[_T],
    *optnames: str,
    default: Any = dataclasses.MISSING,
    metadata: Optional[dict[str, Any]] = None,
) -> Any:
    """Setup a choices field with an optional default choice."""
    if metadata is None:
        metadata = {}
    return arg(
        helpstr,
        *optnames,
        metadata=metadata | {"choices": choices_},
        default=default,
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
    kwargs = {}
    if default is not dataclasses.MISSING:
        kwargs["default"] = default
    if default_factory is not dataclasses.MISSING:
        kwargs["default_factory"] = default_factory

    return arg(
        helpstr,
        metadata=metadata | {"positional": True},
        **kwargs,
    )


# ==============================================================================
# Utilities for specifiying subgroups
# ==============================================================================


def mutually_exclusive_group() -> Any:
    """Setup a mutually exclusive group."""
    return dataclasses.field(metadata={"mutually_exclusive": True})
