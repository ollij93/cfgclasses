# Config Classes (cfgclasses)

| | |
| --- | --- |
| CI/CD | [![CI - Test](https://github.com/ollij93/cfgclasses/actions/workflows/python.yml/badge.svg)](https://github.com/ollij93/cfgclasses/actions/workflows/python.yml) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/cfgclasses.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/cfgclasses/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/cfgclasses.svg?color=blue&label=Downloads&logo=pypi&logoColor=gold)](https://pypi.org/project/cfgclasses/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cfgclasses.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/cfgclasses/) |
| Meta | [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![linting - pylint](https://img.shields.io/badge/lint-pylint-blue.svg)](https://github.com/pylint-dev/pylint) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) |

-----

Strongly typed tool configuration classes for argument parsing.

ConfigClasses are representations of a python tools CLI configuration options built on [dataclasses](https://docs.python.org/3/library/dataclasses.html). This allows individual tools to focus on specifying their configuration structure without the overhead of interacting with argparse and the typeless Namespace it returns.

## Installation

```sh
pip install cfgclasses
```

## Features

* Simple class definitions using dataclasses
* Nested config and tool submodes reduce code repetition
* Mutually exclusive groups support
* Validation functions for reliable verification of config

## License

CFG-Classes is distributed under the terms of the [MIT](LICENSE) license.
