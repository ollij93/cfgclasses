"""Unit-tests for the configclass module."""

import dataclasses
from typing import Optional

import pytest

from cfgclasses import (
    arg,
    mutually_exclusive,
    parse_args,
    parse_args_with_submodes,
    parse_known_args,
    parse_known_args_with_submodes,
    validator,
)

def test_type_handling() -> None:
    """Test the use of various basic types."""
    @dataclasses.dataclass
    class TestConfig:
        """Config for the type handling tests."""

        anum: int = arg("A simple integer field")
        afloat: float = arg("A simple float field")
        astring: str = arg("A simple string field")
        abool: bool = arg("A simple boolean field")
        anum_list: list[int] = arg("A simple list of integers field")
        astring_list: list[str] = arg("A simple list of strings field")

    assert parse_args(TestConfig, [
        "--anum",
        "1",
        "--afloat",
        "1.0",
        "--astring",
        "test",
        "--abool",
        "--anum-list",
        "1",
        "2",
        "3",
        "--astring-list",
        "test",
        "test2",
    ]) == TestConfig(
        anum=1,
        afloat=1.0,
        astring="test",
        abool=True,
        anum_list=[1, 2, 3],
        astring_list=["test", "test2"],
    )


def test_mutually_exclusive() -> None:
    """Test the use of mutually exclusive groups."""

    @mutually_exclusive
    @dataclasses.dataclass
    class MEGroupConfig:
        """Config for mutually exclusive options relating to A."""

        anum: int = arg("A simple integer field", default=0)
        apple: str = arg("A simple string field", default="no")

    @dataclasses.dataclass
    class TopLevelConfig:
        """Top level config class containing the mutually exclusive group."""

        a_opts: MEGroupConfig

    # Check the indiviual fields can be set
    assert parse_args(
        TopLevelConfig, ["--anum", "10000"]
    ).a_opts == MEGroupConfig(anum=10000)
    assert parse_args(
        TopLevelConfig, ["--apple", "sauce"]
    ).a_opts == MEGroupConfig(apple="sauce")
    # Check that setting both fields fails
    with pytest.raises(SystemExit):
        parse_args(TopLevelConfig, ["--anum", "1", "--apple", "sauce"])


def test_submodes() -> None:
    """Test the use of submodes."""

    @dataclasses.dataclass
    class SubmodeA:
        """Config for the submode A."""

        anum: int = arg("A simple integer field")

    @dataclasses.dataclass
    class SubmodeB:
        """Config for the submode B."""

        bnum: int = arg("A simple integer field")

    @dataclasses.dataclass
    class TopLevelConfig:
        """Top level config class containing the submodes."""

        debug: bool = arg("Enable debug mode")

    submodes = {
        "a": SubmodeA,
        "b": SubmodeB,
    }

    # Check successful specification of submode A
    assert parse_args_with_submodes(
        TopLevelConfig, ["a", "--anum", "10000"], submodes
    ) == (TopLevelConfig(debug=False), SubmodeA(anum=10000))
    # Check successful specification of submode B
    assert parse_args_with_submodes(
        TopLevelConfig, ["b", "--bnum", "10000"], submodes
    ) == (TopLevelConfig(debug=False), SubmodeB(bnum=10000))

    # Check the top level options can be specified
    assert parse_args_with_submodes(
        TopLevelConfig, ["--debug", "a", "--anum", "10000"], submodes
    ) == (TopLevelConfig(debug=True), SubmodeA(anum=10000))

    # Check that specifying neither submode fails
    with pytest.raises(SystemExit):
        parse_args_with_submodes(TopLevelConfig, [], submodes)

    # Check that specifying both submodes fails
    with pytest.raises(SystemExit):
        parse_args_with_submodes(
            TopLevelConfig,
            ["a", "b", "--anum", "10000", "--bnum", "10000"],
            submodes,
        )


def test_unknown_args() -> None:
    """Test the handling of unknown arguments both with and without submodes."""

    @dataclasses.dataclass
    class TopLevelConfig:
        """Top level config class containing the submodes."""

        debug: bool = arg("Enable debug mode")

    # Check the unknown args handling without submodes
    assert parse_known_args(
        TopLevelConfig, ["--debug", "--unknown", "arg"]
    ) == (TopLevelConfig(debug=True), ["--unknown", "arg"])

    @dataclasses.dataclass
    class SubmodeA:
        """Config for the submode A."""

        anum: int = arg("A simple integer field")

    @dataclasses.dataclass
    class SubmodeB:
        """Config for the submode B."""

        bnum: int = arg("A simple integer field")

    submodes = {
        "a": SubmodeA,
        "b": SubmodeB,
    }

    # Check the same but with submodes enabled
    assert parse_known_args_with_submodes(
        TopLevelConfig,
        ["--debug", "a", "--anum", "10000", "--unknown", "arg"],
        submodes,
    ) == (
        TopLevelConfig(debug=True),
        SubmodeA(anum=10000),
        ["--unknown", "arg"],
    )


def test_validation_simple() -> None:
    """Test the use of validation functions."""

    @dataclasses.dataclass
    class ValidationConfig:
        """Config for the validation tests."""

        anum: int = arg("A simple integer field")

        @validator
        def validate_my_config(self) -> None:
            """Validate the config class instance raising a ValueError if invalid."""
            if self.anum < 0:
                raise ValueError("anum must be >= 0")

    # Check that validation fails
    with pytest.raises(SystemExit):
        parse_args(ValidationConfig, ["--anum", "-1"])

    # Check that validation succeeds
    assert parse_args(ValidationConfig, ["--anum", "1"]) == ValidationConfig(
        anum=1
    )


def test_validation_nested() -> None:
    """Test the use of validation functions in nested config classes."""

    @dataclasses.dataclass
    class ValidationConfig:
        """Config for the validation tests."""

        anum: int = arg("A simple integer field")

        @validator
        def validate_inner_config(self) -> None:
            """Validate the config class instance raising a ValueError if invalid."""
            if self.anum < 0:
                raise ValueError("anum must be >= 0")

    @dataclasses.dataclass
    class TopLevelConfig:
        """Top level config class containing the validation config."""

        validation: ValidationConfig

    # Check that validation fails
    with pytest.raises(SystemExit):
        parse_args(TopLevelConfig, ["--anum", "-1"])

    # Check that validation succeeds
    assert parse_args(TopLevelConfig, ["--anum", "1"]) == TopLevelConfig(
        ValidationConfig(anum=1)
    )
