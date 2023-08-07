"""Field types module providing helper functions for defining fields."""
import dataclasses
from typing import Any, Iterable


def simplefield(helpstr: str, *, default: Any = None) -> Any:
    """Setup a simple field with a help string and optionally a default value."""
    kwargs = {}
    if default is not None:
        kwargs["default"] = default
    return dataclasses.field(metadata={"help": helpstr}, **kwargs)


def store_truefield(helpstr: str) -> Any:
    """Setup a boolean field that doesn't take a value such a '--debug'."""
    return dataclasses.field(metadata={"help": helpstr}, default=False)


def optionalfield(helpstr: str) -> Any:
    """Setup an optional field which defaults to None."""
    return dataclasses.field(metadata={"help": helpstr}, default=None)


def choicesfield(
    helpstr: str, choices: Iterable[Any], *, default: Any = None
) -> Any:
    """Setup a choices field with an optional default choice."""
    kwargs = {}
    if default is not None:
        kwargs["default"] = default
    return dataclasses.field(
        metadata={"help": helpstr, "choices": choices},
        **kwargs,
    )


def mutually_exclusive_group() -> Any:
    """Setup a mutually exclusive group."""
    return dataclasses.field(metadata={"mutually_exclusive": True})
