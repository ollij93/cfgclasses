"""Main entrypoint of this package."""
import argparse
import sys


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse the CLI arguments."""
    parser = argparse.ArgumentParser()

    # Add arguments here
    parser.add_argument("--name", default="World", help="who to greet")

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    """Main entry point of this script."""
    args = _parse_args(argv)
    print(f"Hello, {args.name}!")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
