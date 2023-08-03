"""Tests for the main module."""

from typing import Any

from .. import __main__ as main


def test_no_args(capsys: Any) -> None:
    """Test the main flow with no CLI arguments."""
    main.main([])
    stdout, stderr = capsys.readouterr()
    assert stdout == "Hello, World!\n"
    assert stderr == ""


def test_with_name(capsys: Any) -> None:
    """Test the main flow with a name provided on the CLI."""
    main.main(["--name", "Olli"])
    stdout, stderr = capsys.readouterr()
    assert stdout == "Hello, Olli!\n"
    assert stderr == ""
