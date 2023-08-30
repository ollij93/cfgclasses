"""Example script using the validation feature of cfgclasses."""
import dataclasses
import sys

from cfgclasses import ConfigClass, arg


@dataclasses.dataclass
class Config(ConfigClass):
    """Config class for this example script."""

    natural: int = arg("A natural number")

    def validate(self) -> None:
        """Validate the provided number is a natural number."""
        if self.natural < 0:
            raise ValueError("natural numbers must be >= 0")

    def run(self) -> None:
        """Main method of this example script."""
        print(f"validated natural number: {self.natural}")


if __name__ == "__main__":
    config = Config.parse_args(sys.argv[1:], prog="validation.py")
    config.run()
