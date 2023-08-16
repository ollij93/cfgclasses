"""Module defining the ConfigGroup class."""
import dataclasses


@dataclasses.dataclass
class ConfigGroup:
    """
    Class for wrapping a set of config options to build cfgclasses from.
    """
