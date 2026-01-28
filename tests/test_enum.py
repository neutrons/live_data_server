import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parents[1]))
from src.config.instruments import Instruments


@pytest.mark.parametrize("instrument", ["fake_instrument", "ref_m"])
def test_enum(instrument):
    assert Instruments.has_value(instrument) == (instrument == "ref_m")
