"""Example script not using cfgclasses and doing validation manually."""

import argparse
import sys


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse the arguments using the given prog name."""
    parser = argparse.ArgumentParser(prog="validation_argparse.py")
    parser.add_argument("--natural", type=int, help="A natural number")
    args = parser.parse_args(argv)
    if args.natural < 0:
        parser.error("natural numbers must be >= 0")
    return args


def main(argv: list[str]) -> None:
    """Main method of this example script."""
    args = _parse_args(argv)
    print(f"validated natural number: {args.natural}")


if __name__ == "__main__":
    main(sys.argv[1:])
