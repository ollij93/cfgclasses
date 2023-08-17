"""Example script using the validation feature of cfgclasses."""
import dataclasses
import sys

import cfgclasses as cfg


@dataclasses.dataclass
class Config(cfg.ConfigClass):
    """Config class for this example script."""

    natural: int = cfg.simple("A natural number")

    def validate(self) -> None:
        """Validate the provided number is a natural number."""
        if self.natural < 0:
            raise ValueError("natural numbers must be >= 0")


def main(argv: list[str]) -> None:
    """Main method of this example script."""
    config = Config.parse_args(argv, prog="validation.py")
    print(f"validated natural number: {config.natural}")


if __name__ == "__main__":
    main(sys.argv[1:])
