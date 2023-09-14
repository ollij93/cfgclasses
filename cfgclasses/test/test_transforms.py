"""Tests for the model transforms."""

import json
import pickle
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .. import ConfigClass, arg
from ..transforms import filebytes, filetext, jsonfile, picklefile


def test_file_content() -> None:
    """Test the file content transform usage."""

    @dataclass
    class TestConfig(ConfigClass):
        """Test Config"""

        data: str = arg("Input data", transform=filetext, transform_type=Path)
        bits: bytes = arg(
            "Input binary data", transform=filebytes, transform_type=Path
        )

    content = "ABC\nDEF\nGHI\n"
    with tempfile.NamedTemporaryFile(mode="w") as tmp:
        tmp.write(content)
        tmp.flush()

        config = TestConfig.parse_args(
            ["--data", tmp.name, "--bits", tmp.name]
        )
        assert config.data == content
        assert config.bits == content.encode("utf-8")


def test_json() -> None:
    """Test the JSON file transform usage."""

    @dataclass
    class TestConfig(ConfigClass):
        """Test Config"""

        data: Any = arg("Input data", transform=jsonfile, transform_type=Path)

    content = {"ABC": "DEF", "GHI": 123}
    with tempfile.NamedTemporaryFile(mode="w") as tmp:
        tmp.write(json.dumps(content))
        tmp.flush()

        config = TestConfig.parse_args(["--data", tmp.name])
        assert config.data == content


def test_pickle() -> None:
    """Test the pickle file transform usage."""

    @dataclass
    class TestConfig(ConfigClass):
        """Test Config"""

        data: Any = arg(
            "Input data", transform=picklefile, transform_type=Path
        )

    content = {"ABC": "DEF", "GHI": 123}
    with tempfile.NamedTemporaryFile(mode="wb") as tmp:
        tmp.write(pickle.dumps(content))
        tmp.flush()

        config = TestConfig.parse_args(["--data", tmp.name])
        assert config.data == content
