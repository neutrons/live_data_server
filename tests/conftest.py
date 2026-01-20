import hashlib
import os
import sys

import pytest

this_module_path = sys.modules[__name__].__file__


@pytest.fixture(scope="module")
def data_server():
    """Object containing info and functionality for data files.

    It assumes the data files are stored under directory `data/`, located
    under the same directory as this module.
    """

    class _DataServe(object):
        _directory = os.path.join(os.path.dirname(this_module_path), "data")

        @property
        def directory(self):
            """Directory where to find the data files"""
            return self._directory

        def path_to(self, basename):
            """Absolute path to a data file"""
            file_path = os.path.join(self._directory, basename)
            if not os.path.isfile(file_path):
                raise IOError(f"File {basename} not found in data directory {self._directory}")
            return file_path

    return _DataServe()


def generate_key(instrument, run_id):
    """
    Generate a secret key for a run on a given instrument
    Used to simulate clients sending GET-requests using a secret key
    @param instrument: instrument name
    @param run_id: run number
    """
    secret_key = os.environ.get("LIVE_PLOT_SECRET_KEY")
    if secret_key is None or len(secret_key) == 0:
        return None

    return hashlib.sha1(f"{instrument.upper()}{secret_key}{run_id}".encode("utf-8")).hexdigest()
