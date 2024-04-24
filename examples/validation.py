"""Example script using the validation feature of cfgclasses."""
import dataclasses
import sys

from cfgclasses import arg, parse_args, validator


@dataclasses.dataclass
class Config:
    """Config class for this example script."""

    natural: int = arg("A natural number")

    @validator
    def validate(self) -> None:
        """Validate the provided number is a natural number."""
        if self.natural < 0:
            raise ValueError("natural numbers must be >= 0")

    def run(self) -> None:
        """Main method of this example script."""
        print(f"validated natural number: {self.natural}")


if __name__ == "__main__":
    config = parse_args(Config, sys.argv[1:], prog="validation.py")
    config.run()
