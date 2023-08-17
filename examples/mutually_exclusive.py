"""Example script using the mutually exclusive group feature of cfgclasses."""
import dataclasses
import logging
import sys

import cfgclasses as cfg


@dataclasses.dataclass
class LogLevel(cfg.ConfigClass):
    """Config group for specifying the log level."""

    debug: bool = cfg.store_true("Enable debug logging")
    quiet: bool = cfg.store_true("Only output errors")


@dataclasses.dataclass
class Config(cfg.ConfigClass):
    """Config class for this example script."""

    loglevel: LogLevel = cfg.mutually_exclusive_group()


def main(argv: list[str]) -> None:
    """Main method of this example script."""
    config = Config.parse_args(argv, prog="mutually_exclusive.py")

    if config.loglevel.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif config.loglevel.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.debug("Debug logging enabled")
    logging.info("Info logging enabled")
    logging.error("Error logging enabled")


if __name__ == "__main__":
    main(sys.argv[1:])
