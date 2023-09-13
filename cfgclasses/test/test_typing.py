"""Testing that expected typing errors are raised by mypy."""

from dataclasses import dataclass

import pytest

from cfgclasses import ConfigClass, arg

# =============================================================================
# The test cases in this file are run both as regular test cases and as
# mypy_testing cases. Regular asserts can be made within the cases if needed.
# =============================================================================


@pytest.mark.mypy_testing
def test_invalid_transform() -> None:
    """Test that invalid types in transforms are identified."""

    def typed_transform(i: int) -> str:
        return str(i)

    @dataclass
    class TestClass(ConfigClass):
        """Test class."""

        # Invalid assignment type
        field_a: int = arg(  # E: [assignment]
            "Help", transform_type=int, transform=typed_transform
        )
        # Invalid assignment type with lambda
        field_b: str = arg(  # E: [assignment]
            "Help", transform_type=int, transform=lambda x: x
        )

        # Missing transform_type
        field_c: str = arg("Help", transform=lambda x: x)  # O: [call-overload]
        # Missing transform function
        field_d: str = arg(  # O: [call-overload]
            "Help",
            transform_type=str,
        )

        # Mismatching transform_type and transform
        field_e: str = arg(
            "Help",
            transform_type=float,
            transform=typed_transform,  # E: [arg-type]
        )

    # To keep linting and coverage happy use the class we've just defined
    # and call the transform function to cover the missing line.
    TestClass(1, "B", "C", "D", "E")
    typed_transform(0)


@pytest.mark.mypy_testing
def test_invalid_choices() -> None:
    """Test that invalid types in choices are identified."""

    @dataclass
    class TestClass(ConfigClass):
        """Test class."""

        field: str = arg(  # E: [assignment]
            "Help",
            choices=[1, 2, 3],
        )

    TestClass("A")


@pytest.mark.mypy_testing
def test_invalid_default() -> None:
    """Test that invalid types in defaults are identified."""

    @dataclass
    class TestClass(ConfigClass):
        """Test class."""

        field: str = arg(  # E: [assignment]
            "Help",
            default=1,
        )
        field2: str = arg(  # E: [assignment]
            "Help",
            default_factory=lambda: 1,
        )

    TestClass("A", "B")


@pytest.mark.mypy_testing
def test_incompatible_default_args() -> None:
    """Test that default and default_factory can't both be set."""

    @dataclass
    class TestClass(ConfigClass):
        """Test class."""

        field_a: str = arg(  # O: [call-overload]
            "Help", default="", default_factory=lambda: ""
        )
        field_b: str = arg(  # O: [call-overload]
            "Help", positional=True, default="", default_factory=lambda: ""
        )

    TestClass("A", "B")


@pytest.mark.mypy_testing
def test_positional_optnames() -> None:
    """Test that option names can't be specified with a positional argument."""

    @dataclass
    class TestClass(ConfigClass):
        """Test class."""

        field_a: str = arg(  # O: [call-overload]
            "Help", "FIELD_A", positional=True
        )

    TestClass("A")