# The nature of this testing means we need to disable some linter messages in
# this file. Do this globally for the file rather than case by case.
"""Testing that expected typing errors are raised by mypy."""

from dataclasses import dataclass

import pytest

from cfgclasses import ConfigClass, arg


@pytest.mark.mypy_testing
def test_invalid_transform() -> None:
    """Test that invalid types are rejected."""

    @dataclass
    class TestClass(ConfigClass):
        """Test class."""

        field: str = arg(  # E: [assignment]
            "Help", transform_type=int, transform=lambda x: x
        )

    TestClass("A")
