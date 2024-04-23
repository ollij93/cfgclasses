"""Example script using the mutually exclusive group feature of cfgclasses."""
import dataclasses
import logging
import sys

from cfgclasses import arg, parse_args, mutually_exclusive


@mutually_exclusive
@dataclasses.dataclass
class LogLevel:
    """Config group for specifying the log level."""

    debug: bool = arg("Enable debug logging")
    quiet: bool = arg("Only output errors")

    def logging_level(self) -> int:
        """Return the logging level specified by this config group."""
        if self.debug:
            return logging.DEBUG
        if self.quiet:
            return logging.ERROR
        return logging.INFO


@dataclasses.dataclass
class Config:
    """Config class for this example script."""

    loglevel: LogLevel

    def run(self) -> None:
        """Main method of this example script."""
        logging.basicConfig(level=self.loglevel.logging_level())
        logging.debug("Debug logging enabled")
        logging.info("Info logging enabled")
        logging.error("Error logging enabled")


if __name__ == "__main__":
    config = parse_args(Config, sys.argv[1:], prog="mutually_exclusive.py")
    config.run()
