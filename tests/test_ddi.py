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

    # does it give the right description
    assert cps_ddi.get_variable_info("year").description == "YEAR reports the year in which the survey was conducted.  YEARP is repeated on person records."

    # does it return the name
    assert cps_ddi.get_variable_info("year").name == "YEAR"

    # codes
    assert cps_ddi.get_variable_info("month").codes == {"January": 1,
                                                        "February": 2,
                                                        "March": 3,
                                                        "April": 4,
                                                        "May": 5,
                                                        "June": 6,
                                                        "July": 7,
                                                        "August": 8,
                                                        "September": 9,
                                                        "October": 10,
                                                        "November": 11,
                                                        "December": 12}

    # And does it raise a ValueError if the variable does not exist?
    with pytest.raises(ValueError):
        cps_ddi.get_variable_info("foo")
