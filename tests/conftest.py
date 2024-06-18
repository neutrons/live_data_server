# 3rd-party imports
# standard imports
import os
import sys

import pytest

this_module_path = sys.modules[__name__].__file__


@pytest.fixture(scope="module")
def data_server():
    r"""Object containing info and functionality for data files.

    It assumes the data files are stored under directory `data/`, located
    under the same directory as this module.
    """

    class _DataServe(object):
        _directory = os.path.join(os.path.dirname(this_module_path), "data")

        @property
        def directory(self):
            r"""Directory where to find the data files"""
            return self._directory

        def path_to(self, basename):
            r"""Absolute path to a data file"""
            file_path = os.path.join(self._directory, basename)
            if not os.path.isfile(file_path):
                raise IOError("File {basename} not found in data directory {self._directory}")
            return file_path

    return _DataServe()
