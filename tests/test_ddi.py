from pathlib import Path

import pandas as pd
import pytest

from ipumspy import ddi, readers


@pytest.fixture(scope="module")
def cps_ddi(fixtures_path: Path) -> ddi.Codebook:
    return readers.read_ipums_ddi(fixtures_path / "cps_00006.xml")


@pytest.fixture(scope="module")
def cps_df(fixtures_path: Path, cps_ddi: ddi.Codebook) -> pd.DataFrame:
    return readers.read_microdata(cps_ddi, fixtures_path / "cps_00006.csv.gz")


def test_get_variable_info(cps_ddi: ddi.Codebook, cps_df: pd.DataFrame):
    # Does it retrieve the appropriate variable?
    assert cps_ddi.get_variable_info("YEAR").id == "YEAR"

    # Even if the name is not UPPERCASE?
    assert cps_ddi.get_variable_info("year").id == "YEAR"

    # does it give the right codes
    assert cps_ddi.get_variable_info("year").codes == {'1962': 1962}

    # does it give the right description
    assert cps_ddi.get_variable_info("year").description == "Survey year"

    # And does it raise a ValueError if the variable does not exist?
    with pytest.raises(ValueError):
        cps_ddi.get_variable_info("foo")
