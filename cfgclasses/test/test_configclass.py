"""Unit-tests for the configclass module."""
import dataclasses

import pytest

from cfgclasses import ConfigClass, MutuallyExclusiveConfigClass, arg


def test_mutually_exclusive() -> None:
    """Test the use of mutually exclusive groups."""

    @dataclasses.dataclass
    class MEGroupConfig(MutuallyExclusiveConfigClass):
        """Config for mutually exclusive options relating to A."""

        anum: int = arg("A simple integer field", default=0)
        apple: str = arg("A simple string field", default="no")

    @dataclasses.dataclass
    class TopLevelConfig(ConfigClass):
        """Top level config class containing the mutually exclusive group."""

        a_opts: MEGroupConfig

    # Check the indiviual fields can be set
    assert TopLevelConfig.parse_args(
        ["--anum", "10000"]
    ).a_opts == MEGroupConfig(anum=10000)
    assert TopLevelConfig.parse_args(
        ["--apple", "sauce"]
    ).a_opts == MEGroupConfig(apple="sauce")
    # Check that setting both fields fails
    with pytest.raises(SystemExit):
        TopLevelConfig.parse_args(["--anum", "1", "--apple", "sauce"])


def test_submodes() -> None:
    """Test the use of submodes."""

    @dataclasses.dataclass
    class SubmodeA(ConfigClass):
        """Config for the submode A."""

        anum: int = arg("A simple integer field")

    @dataclasses.dataclass
    class SubmodeB(ConfigClass):
        """Config for the submode B."""

        bnum: int = arg("A simple integer field")

    @dataclasses.dataclass
    class TopLevelConfig(ConfigClass):
        """Top level config class containing the submodes."""

        debug: bool = arg("Enable debug mode")

    submodes = {
        "a": SubmodeA,
        "b": SubmodeB,
    }

    # Check successful specification of submode A
    assert TopLevelConfig.parse_args_with_submodes(
        ["a", "--anum", "10000"], submodes
    ) == (TopLevelConfig(debug=False), SubmodeA(anum=10000))
    # Check successful specification of submode B
    assert TopLevelConfig.parse_args_with_submodes(
        ["b", "--bnum", "10000"], submodes
    ) == (TopLevelConfig(debug=False), SubmodeB(bnum=10000))

    # Check the top level options can be specified
    assert TopLevelConfig.parse_args_with_submodes(
        ["--debug", "a", "--anum", "10000"], submodes
    ) == (TopLevelConfig(debug=True), SubmodeA(anum=10000))

    # Check that specifying neither submode fails
    with pytest.raises(SystemExit):
        TopLevelConfig.parse_args_with_submodes([], submodes)

    # Check that specifying both submodes fails
    with pytest.raises(SystemExit):
        TopLevelConfig.parse_args_with_submodes(
            ["a", "b", "--anum", "10000", "--bnum", "10000"], submodes
        )


def test_validation_simple() -> None:
    """Test the use of validation functions."""

    @dataclasses.dataclass
    class ValidationConfig(ConfigClass):
        """Config for the validation tests."""

        anum: int = arg("A simple integer field")

        def validate(self) -> None:
            """Validate the config class instance raising a ValueError if invalid."""
            if self.anum < 0:
                raise ValueError("anum must be >= 0")

    # Check that validation fails
    with pytest.raises(SystemExit):
        ValidationConfig.parse_args(["--anum", "-1"])

    # Check that validation succeeds
    assert ValidationConfig.parse_args(["--anum", "1"]) == ValidationConfig(
        anum=1
    )


def test_validation_nested() -> None:
    """Test the use of validation functions in nested config classes."""

    @dataclasses.dataclass
    class ValidationConfig(ConfigClass):
        """Config for the validation tests."""

        anum: int = arg("A simple integer field")

        def validate(self) -> None:
            """Validate the config class instance raising a ValueError if invalid."""
            if self.anum < 0:
                raise ValueError("anum must be >= 0")

    @dataclasses.dataclass
    class TopLevelConfig(ConfigClass):
        """Top level config class containing the validation config."""

        validation: ValidationConfig

    # Check that validation fails
    with pytest.raises(SystemExit):
        TopLevelConfig.parse_args(["--anum", "-1"])

    # Check that validation succeeds
    assert TopLevelConfig.parse_args(["--anum", "1"]) == TopLevelConfig(
        ValidationConfig(anum=1)
    )
