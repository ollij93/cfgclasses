"""Common transform helpers module."""
import json
import pickle
from pathlib import Path
from typing import Any

__all__ = (
    "binarycontent",
    "filecontent",
    "jsoncontent",
)

DEFAULT_ENCODING = "utf-8"


# =============================================================================
# File content transforms
# =============================================================================
def binarycontent(argval: Path | str) -> bytes:
    """Tranform a file path argument into its contents."""
    return Path(argval).read_bytes()


def filecontent(argval: Path | str) -> str:
    """Tranform a file path argument into its contents."""
    return Path(argval).read_text(DEFAULT_ENCODING)


def jsoncontent(argval: Path | str) -> Any:
    """Tranform a file path argument into its json encoded contents."""
    return json.loads(Path(argval).read_text(DEFAULT_ENCODING))


def picklecontent(argval: Path | str) -> Any:
    """Tranform a file path argument into its pickle encoded contents."""
    return pickle.loads(Path(argval).read_bytes())
