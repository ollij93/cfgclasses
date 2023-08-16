"""Unit-tests for the configclass module."""
import argparse
import dataclasses

import pytest

from cfgclasses import (
    ConfigClass,
    ConfigSubmode,
    mutually_exclusive_group,
    simple,
    store_true,
)


def test_mutually_exclusive() -> None:
    """Test the use of mutually exclusive groups."""

    @dataclasses.dataclass
    class MEGroupConfig(ConfigClass):
        """Config for mutually exclusive options relating to A."""

        anum: int = simple("A simple integer field", default=0)
        apple: str = simple("A simple string field", default="no")

    @dataclasses.dataclass
    class TopLevelConfig(ConfigClass):
        """Top level config class containing the mutually exclusive group."""

        a_opts: MEGroupConfig = mutually_exclusive_group()

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

        anum: int = simple("A simple integer field")

    @dataclasses.dataclass
    class SubmodeB(ConfigClass):
        """Config for the submode B."""

        bnum: int = simple("A simple integer field")

    @dataclasses.dataclass
    class TopLevelConfig(ConfigClass):
        """Top level config class containing the submodes."""

        debug: bool = store_true("Enable debug mode")

    submodes = [ConfigSubmode("a", SubmodeA), ConfigSubmode("b", SubmodeB)]

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
    with pytest.raises(argparse.ArgumentError):
        TopLevelConfig.parse_args_with_submodes([], submodes)

    # Check that specifying both submodes fails
    with pytest.raises(SystemExit):
        TopLevelConfig.parse_args_with_submodes(
            ["a", "b", "--anum", "10000", "--bnum", "10000"], submodes
        )
