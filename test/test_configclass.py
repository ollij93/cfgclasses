"""Unit-tests for the configclass module."""
import argparse
import dataclasses
from pathlib import Path

import pytest

from configclasses import (
    ConfigClass,
    ConfigSubmode,
    mutually_exclusive_group,
    simplefield,
    store_truefield,
)


# ==========================================================================
# Fixtures for mutually-exclusive group testing
# ==========================================================================
@dataclasses.dataclass
class MEGroupConfig(ConfigClass):
    """Config for mutually exclusive options relating to A."""

    anum: int = simplefield("A simple integer field", default=0)
    apple: str = simplefield("A simple string field", default="no")


@dataclasses.dataclass
class METopLevelConfig(ConfigClass):
    """Top level config class containing the mutually exclusive group."""

    a_opts: MEGroupConfig = mutually_exclusive_group()


class TestMutuallyExclusiveGroup:
    """Test the use of mutually exclusive groups."""

    def test_success(self) -> None:
        """Test the indiviual fields can be set in the group."""
        config: METopLevelConfig = METopLevelConfig.parse_args(
            ["--anum", "10000"]
        )
        assert config == METopLevelConfig(a_opts=MEGroupConfig(anum=10000))

        config = METopLevelConfig.parse_args(["--apple", "sauce"])
        assert config == METopLevelConfig(a_opts=MEGroupConfig(apple="sauce"))

    def test_failure(self) -> None:
        """Test that setting both fields fails in the group fails."""
        with pytest.raises(SystemExit):
            METopLevelConfig.parse_args(["--anum", "1", "--apple", "sauce"])


# ==========================================================================
# Fixtures for submode testing
# ==========================================================================
@dataclasses.dataclass
class SubmodeA(ConfigClass):
    """Config for the submode A."""

    anum: int = simplefield("A simple integer field")


@dataclasses.dataclass
class SubmodeB(ConfigClass):
    """Config for the submode B."""

    bnum: int = simplefield("A simple integer field")


@dataclasses.dataclass
class TopLevelConfig(ConfigClass):
    """Top level config class containing the submodes."""

    debug: bool = store_truefield("Enable debug mode")


TEST_SUBMODES = [ConfigSubmode("a", SubmodeA), ConfigSubmode("b", SubmodeB)]


class TestSubmodes:
    """Testing for submode functionality of ConfigClass."""

    def test_submode_selection(self) -> None:
        """Test the simple selection of submodes and using their config."""
        # Check successful specification of submode A
        assert TopLevelConfig.parse_args_with_submodes(
            ["a", "--anum", "10000"], TEST_SUBMODES
        ) == (TopLevelConfig(debug=False), SubmodeA(anum=10000))
        # Check successful specification of submode B
        assert TopLevelConfig.parse_args_with_submodes(
            ["b", "--bnum", "10000"], TEST_SUBMODES
        ) == (TopLevelConfig(debug=False), SubmodeB(bnum=10000))

    def test_top_level_options(self) -> None:
        """Test the specification of top level options when using submodes."""
        assert TopLevelConfig.parse_args_with_submodes(
            ["--debug", "a", "--anum", "10000"], TEST_SUBMODES
        ) == (TopLevelConfig(debug=True), SubmodeA(anum=10000))

    def test_submode_selection_failure(self) -> None:
        """Test that specifying neither submode fails."""
        with pytest.raises(argparse.ArgumentError):
            TopLevelConfig.parse_args_with_submodes([], TEST_SUBMODES)

    def test_submode_selection_duplicates(self) -> None:
        """Test that specifying both submodes fails."""
        with pytest.raises(SystemExit):
            TopLevelConfig.parse_args_with_submodes(
                ["a", "b", "--anum", "10000", "--bnum", "10000"], TEST_SUBMODES
            )


# ==========================================================================
# Fixtures for user config file testing
# ==========================================================================
@dataclasses.dataclass
class FromUserConfig(ConfigClass):
    """Config that will be loaded from yaml."""

    anum: int = simplefield("A simple integer field", default=0)
    astr: str = simplefield("A simple string field", default="no")
    alst: list[str] = simplefield(
        "A list of strings field", default_factory=list
    )


class TestUserConfig:
    """Testing for loading user config files."""

    def test_success(self) -> None:
        """Test that loading a user config file works."""
        assert FromUserConfig.parse_args(
            [], useryamlconfig=Path("test/fixtures/test_config.yaml")
        ) == FromUserConfig(anum=123, astr="test_str", alst=["a", "b", "c"])
