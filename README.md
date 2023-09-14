# Config Classes (cfgclasses)

| | |
| --- | --- |
| CI/CD | [![CI - Test](https://github.com/ollij93/cfgclasses/actions/workflows/python.yml/badge.svg)](https://github.com/ollij93/cfgclasses/actions/workflows/python.yml) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/cfgclasses.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/cfgclasses/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/cfgclasses.svg?color=blue&label=Downloads&logo=pypi&logoColor=gold)](https://pypi.org/project/cfgclasses/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cfgclasses.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/cfgclasses/) |
| Meta | [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![linting - pylint](https://img.shields.io/badge/lint-pylint-blue.svg)](https://github.com/pylint-dev/pylint) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) |

-----

Strongly typed tool configuration classes for argument parsing.

ConfigClasses are representations of a python tools CLI configuration options built on [dataclasses](https://docs.python.org/3/library/dataclasses.html). This allows individual tools to focus on specifying their configuration structure without the overhead of interacting with argparse and the typeless Namespace it returns.

See the [documnentation](https://ollij93.github.io/cfgclasses/) for full user guides and API references.

## Installation

```sh
pip install cfgclasses
```

## Features

* Simple class definitions using dataclasses
* Nested config and tool submodes reduce code repetition
* Mutually exclusive groups support
* Validation functions for reliable verification of config
* Argument transformations reducing repetition of common patterns (e.g. reading contents of a file)

## Example Usage

The following shows a simple script setup using a Config Class.

```python3
import dataclasses
import sys
from cfgclasses import ConfigClass, arg, optional
from pathlib import Path
from typing import Optional

@dataclasses.dataclass
class Config(ConfigClass):
    # Simple options are required on the CLI
    intopt: int = arg("A simple integer field")
    inpath: Path = arg("A required Path field")

    # Optional fields default to None when not specified
    outpath: Optional[Path] = optional("An optional Path field")

    # Can specify custom default or default_factory values
    stropt: str = arg("A string field with a default", default="X")

    # The authors preference is to put run modes on the config classes.
    # This is entirely optional, and main() methods that take in the Config
    # object as their only arg is a perfectly sensible alternative.
    def run(self) -> None:
        """Main entry point of this script."""
        ...

if __name__ == '__main__':
    config = Config.parse_args(sys.argv[1:], prog="example")
    config.run()
```

The `-h` output from this script is:

```txt
usage: example [-h] --intopt INTOPT --inpath INPATH [--outpath OUTPATH] [--stropt STROPT]

options:
  -h, --help         show this help message and exit

  --intopt INTOPT    A simple integer field
  --inpath INPATH    A required Path field
  --outpath OUTPATH  An optional Path field
  --stropt STROPT    A string field with a default
```

This same script implemented in argparse would look like this:

```python3
import argparse
import sys
from pathlib import Path

def _parse_args(argv: list[str]):
    parser = argparse.ArgumentParser(prog="example")
    # In argparse options default to None unless you specified they're required.
    # Help messages are optional in argparse, but required in cfgclasses.
    parser.add_argument("--intopt", type=int, help="A simple integer field", required=True)
    parser.add_arugment("--inpath", type=Path, help="A required Path field", required=True)

    # Optional fields are the default in argparse, so type is actually Optional[Path]
    parser.add_argument("--outpath", type=Path, help="An optional Path field")

    # Defaults work the same, but there's no default_factory in argparse
    parser.add_argument("--stropt", default=X", help="A string field with a default")

def main(args: argparse.Namespace) -> None:
    """Main entry point of this script."""
    # Note: args here is relatively typeless - if one of the argument types is
    # changed (e.g. from str to Path) mypy will not pick up on this error.
    ...

if __name__ == '__main__':
    args = _parse_args(sys.argv[1:])
    main(args)

```

For further examples see the [examples](examples) subdirectory.

## License

CFG-Classes is distributed under the terms of the [MIT](LICENSE) license.
