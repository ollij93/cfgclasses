"""Module defining the ConfigGroup class."""
import dataclasses
from pathlib import Path

import yaml


@dataclasses.dataclass
class ConfigGroup:
    """
    Class for wrapping a set of config options to build configclasses from.
    """

    def output_yaml(self, path: Path) -> None:
        """Output the config in yaml format to the given path."""
        path.write_text(yaml.dump(dataclasses.asdict(self)))
