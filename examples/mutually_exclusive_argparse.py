"""Example script using the mutually exclusive group feature of cfgclasses."""

import argparse
import logging
import sys


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse the arguments using the given prog name."""
    parser = argparse.ArgumentParser(prog="mutually_exlusive_argparse.py")
    me_group = parser.add_mutually_exclusive_group()
    me_group.add_argument(
        "--debug", action="store_true", help="Enable debug logging"
    )
    me_group.add_argument(
        "--quiet", action="store_true", help="Only output errors"
    )

    return parser.parse_args(argv)


def main(argv: list[str]) -> None:
    """Main method of this example script."""
    args = _parse_args(argv)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.debug("Debug logging enabled")
    logging.info("Info logging enabled")
    logging.error("Error logging enabled")


if __name__ == "__main__":
    main(sys.argv[1:])
