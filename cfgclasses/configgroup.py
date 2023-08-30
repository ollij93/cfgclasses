"""Module defining the ConfigGroup class."""
import argparse
import dataclasses


@dataclasses.dataclass
class ConfigGroup:
    """
    Class for wrapping a set of config options to build cfgclasses from.
    """

    @classmethod
    def add_argument_group(
        cls, parser: argparse._ActionsContainer
    ) -> argparse._ActionsContainer:
        """
        Add an argument group to the given parser.

        The added group will have the fields of this class added to it.
        """
        return parser.add_argument_group()

    def validate(self) -> None:
        """
        Validate the config class instance raising a ValueError if invalid.
        """


def _validate_nested(value: ConfigGroup) -> None:
    """Utility method to invoke the validation methods on nested classes."""
    for attr in dir(value):
        subvalue = getattr(value, attr)
        if isinstance(subvalue, ConfigGroup):
            subvalue.validate()
            _validate_nested(subvalue)


def validate_post_argparse(
    group: "ConfigGroup", parser: argparse.ArgumentParser
) -> None:
    """
    Validate the config class instance raising an argparse error if invalid.

    Unlike the ConfigGroup.validate() method this method handles the nested
    config classes and raises an argparse error if any of the nested classes.

    :param group:
        The group to be validated.
    :param parser:
        The parser used to parse the arguments from which any errors will be
        raised.
    """
    try:
        group.validate()
        _validate_nested(group)
    except ValueError as exc:
        parser.error(str(exc))
