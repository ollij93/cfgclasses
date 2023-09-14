"""
Module defining common transform function patterns.

.. autofunction:: filetext
.. autofunction:: filebytes
.. autofunction:: jsonfile
.. autofunction:: picklefile

"""

import json
import pickle
from pathlib import Path, PurePath
from typing import Any, Union

__all__ = (
    "filetext",
    "filebytes",
    "jsonfile",
    "picklefile",
)


def filetext(filepath: Union[str, PurePath]) -> str:
    """
    Transform function for loading text file contents.

    :param filepath:
        Path of the file to be loaded.
    :return:
        The contents of the file as a string.
    """
    return Path(filepath).read_text(encoding="utf-8")


def filebytes(filepath: Union[str, PurePath]) -> bytes:
    """
    Transform function for loading binary file contents.

    :param filepath:
        Path of the file to be loaded.
    :return:
        The contents of the file as a byte array.
    """
    return Path(filepath).read_bytes()


def jsonfile(filepath: Union[str, PurePath]) -> Any:
    """
    Transform function for loading JSON files.

    :param filepath:
        Path of the file to be loaded.
    :return:
        The loaded JSON contents of the file.
    """
    return json.loads(filetext(filepath))


def picklefile(filepath: Union[str, PurePath]) -> Any:
    """
    Transform function for loading pickle files.

    :param filepath:
        Path of the file to be loaded.
    :return:
        The loaded pickle content of the file.
    """
    return pickle.loads(filebytes(filepath))
