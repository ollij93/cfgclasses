"""Module defining the ConfigGroup class."""

import argparse
import dataclasses
from typing import Callable, TypeVar

_T = TypeVar("_T")

CFG_VALIDATOR_FUNC_ATTR = "__cfgclass_validator_func__"

__all__ = ("validator",)


def validator(func: Callable[[_T], None]) -> Callable[[_T], None]:
    """
    Decorator to mark a function as a validator for a config class.

    :param func: The function to mark as a validator.
    :return: The modified input function.
    """
    setattr(func, CFG_VALIDATOR_FUNC_ATTR, True)
    return func


def _invoke_validators(value: _T) -> None:
    """Invoke the validator function on the given value if it exists."""
    for attr in dir(value):
        subvalue = getattr(value, attr)
        is_validator = getattr(subvalue, CFG_VALIDATOR_FUNC_ATTR, False)
        if is_validator:
            subvalue()


def _validate_nested(value: _T) -> None:
    """Utility method to invoke the validation methods on nested classes."""
    for attr in dir(value):
        # Skip "__" attributes
        if attr.startswith("__"):
            continue

        subvalue = getattr(value, attr)
        if dataclasses.is_dataclass(subvalue):
            _invoke_validators(subvalue)
            _validate_nested(subvalue)


def validate_post_argparse(
    dataclass: _T, parser: argparse.ArgumentParser
) -> None:
    """
    Validate the config class raising an argparse error if invalid.

    :param dataclass:
        The config class to be validated.
    :param parser:
        The parser used to parse the arguments from which any errors will be
        raised.
    """
    try:
        _invoke_validators(dataclass)
        _validate_nested(dataclass)
    except ValueError as exc:
        parser.error(str(exc))
