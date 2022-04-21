from pathlib import Path

import pandas as pd
import numpy as np
import pytest

from ipumspy import ddi, readers


@pytest.fixture(scope="module")
def cps_ddi(fixtures_path: Path) -> ddi.Codebook:
    return readers.read_ipums_ddi(fixtures_path / "cps_00006.xml")


@pytest.fixture(scope="module")
def cps_df(fixtures_path: Path, cps_ddi: ddi.Codebook) -> pd.DataFrame:
    return readers.read_microdata(cps_ddi, fixtures_path / "cps_00006.csv.gz")


@pytest.fixture(scope="function")
def cps_ddi2(fixtures_path: Path) -> ddi.Codebook:
    return readers.read_ipums_ddi(fixtures_path / "tmp/acs_00001.xml")


@pytest.fixture(scope="function")
def cps_df2(fixtures_path: Path, cps_ddi2: ddi.Codebook) -> pd.DataFrame:
    return readers.read_microdata(cps_ddi2, fixtures_path / "tmp/acs_00001.csv.gz")


def test_get_variable_info(cps_ddi: ddi.Codebook, cps_df: pd.DataFrame):
    # Does it retrieve the appropriate variable?
    assert cps_ddi.get_variable_info("YEAR").id == "YEAR"

    # Even if the name is not UPPERCASE?
    assert cps_ddi.get_variable_info("year").id == "YEAR"

    # does it give the right description
    assert (
        cps_ddi.get_variable_info("year").description
        == "YEAR reports the year in which the survey was conducted.  YEARP is repeated on person records."
    )

    # does it return the name
    assert cps_ddi.get_variable_info("year").name == "YEAR"

    # codes
    assert cps_ddi.get_variable_info("month").codes == {
        "January": 1,
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
        "December": 12,
    }

    # And does it raise a ValueError if the variable does not exist?
    with pytest.raises(ValueError):
        cps_ddi.get_variable_info("foo")


def test_get_all_types(cps_ddi: ddi.Codebook, cps_df: pd.DataFrame):

    var_types = {
        "YEAR": "numeric",
        "SERIAL": "numeric",
        "HWTSUPP": "numeric",
        "STATEFIP": "numeric",
        "MONTH": "numeric",
        "PERNUM": "numeric",
        "WTSUPP": "numeric",
        "INCTOT": "numeric",
    }

    assert cps_ddi.get_all_types(type_format="vartype") == var_types

    python_types = {
        "YEAR": int,
        "SERIAL": int,
        "HWTSUPP": float,
        "STATEFIP": int,
        "MONTH": int,
        "PERNUM": int,
        "WTSUPP": float,
        "INCTOT": int,
    }

    assert cps_ddi.get_all_types(type_format="python_type") == python_types
    # always np.float64 due to eventual NaNs.
    numpy_types = {
        "YEAR": np.float64,
        "SERIAL": np.float64,
        "HWTSUPP": np.float64,
        "STATEFIP": np.float64,
        "MONTH": np.float64,
        "PERNUM": np.float64,
        "WTSUPP": np.float64,
        "INCTOT": np.float64,
    }

    assert cps_ddi.get_all_types(type_format="numpy_type") == numpy_types

    pandas_types = {
        "YEAR": pd.Int64Dtype(),
        "SERIAL": pd.Int64Dtype(),
        "HWTSUPP": np.float64,
        "STATEFIP": pd.Int64Dtype(),
        "MONTH": pd.Int64Dtype(),
        "PERNUM": pd.Int64Dtype(),
        "WTSUPP": np.float64,
        "INCTOT": pd.Int64Dtype(),
    }

    assert cps_ddi.get_all_types(type_format="pandas_type") == pandas_types

    pandas_types_efficient = {
        "YEAR": np.float64,
        "SERIAL": np.float64,
        "HWTSUPP": np.float64,
        "STATEFIP": np.float64,
        "MONTH": np.float64,
        "PERNUM": np.float64,
        "WTSUPP": np.float64,
        "INCTOT": np.float64,
    }

    assert (
        cps_ddi.get_all_types(type_format="pandas_type_efficient")
        == pandas_types_efficient
    )

    acceptable_values = [
        "numpy_type",
        "pandas_type",
        "pandas_type_efficient",
        "python_type",
        "vartype",
    ]

    # Does it raise a ValueError if the specified type of format, doesn't match existing attribute?
    with pytest.raises(ValueError):
        cps_ddi.get_all_types(type_format="foo")


@pytest.mark.character_data
def test_get_all_types_with_pyarrow(cps_ddi2: ddi.Codebook, cps_df2: pd.DataFrame):
    # this test can be run with variable INDNAICS from IPUMS USA sample ACS 2020 5% for example. I didn't find
    # character variable for CPS therefore I propose one with ACS data. Since IPUMS terms of use
    # https://www.ipums.org/about/terms requires explicit permission for redistribution of the data, I can't share
    # the data. To run the test just need to create an extract with the variables below and select sample ACS 2020.
    # Place the ddi and csv in tests/fixtures/tmp/ and name them acs_00001.xml, acs_00001.csv.gz respectively.

    pandas_types = {
        "YEAR": pd.Int64Dtype(),
        "SAMPLE": pd.Int64Dtype(),
        "SERIAL": pd.Int64Dtype(),
        "CBSERIAL": pd.Int64Dtype(),
        "HHWT": np.float64,
        "CLUSTER": pd.Int64Dtype(),
        "STRATA": pd.Int64Dtype(),
        "GQ": pd.Int64Dtype(),
        "PERNUM": pd.Int64Dtype(),
        "PERWT": np.float64,
        "INDNAICS": pd.StringDtype(storage="pyarrow"),
    }
    assert (
        cps_ddi2.get_all_types(type_format="pandas_type", string_pyarrow=True)
        == pandas_types
    )

    pandas_types_efficient = {
        "YEAR": np.float64,
        "SAMPLE": np.float64,
        "SERIAL": np.float64,
        "CBSERIAL": np.float64,
        "HHWT": np.float64,
        "CLUSTER": np.float64,
        "STRATA": np.float64,
        "GQ": np.float64,
        "PERNUM": np.float64,
        "PERWT": np.float64,
        "INDNAICS": pd.StringDtype(storage="pyarrow"),
    }

    assert (
        cps_ddi2.get_all_types(type_format="pandas_type_efficient", string_pyarrow=True)
        == pandas_types_efficient
    )

    with pytest.raises(ValueError):
        cps_ddi2.get_all_types(type_format="numpy_type", string_pyarrow=True)

    with pytest.raises(ValueError):
        cps_ddi2.get_all_types(type_format="vartype", string_pyarrow=True)

    with pytest.raises(ValueError):
        cps_ddi2.get_all_types(type_format="python_type", string_pyarrow=True)
