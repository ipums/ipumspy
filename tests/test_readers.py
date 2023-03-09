# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

import gzip
import tempfile
from functools import partial
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import pytest

from ipumspy import readers
from ipumspy.api.extract import BaseExtract, UsaExtract


def _assert_cps_000006(data: pd.DataFrame):
    """Run all the checks for the data frame returned by our readers for rectangular files"""
    assert len(data) == 7668
    assert len(data.columns) == 8
    assert (data["YEAR"].iloc[:5] == 1962).all()
    assert (
        data["HWTSUPP"].iloc[:5]
        == np.array([1475.59, 1475.59, 1475.59, 1597.61, 1706.65])
    ).all()
    assert (data.dtypes.values == np.array([pd.Int64Dtype(), pd.Int64Dtype(), float, pd.Int64Dtype(),
                                            pd.Int64Dtype(), pd.Int64Dtype(), float, pd.Int64Dtype()])).all()
    

def _assert_cps_00421_df(data: pd.DataFrame):
    """Run all the checks for the data frame returned by our readers for hierarchical files"""
    assert len(data) == 339278
    assert len(data.columns) == 14
    assert (data["YEAR"].iloc[:5] == 2022).all()
    assert (
        data["HWTSUPP"].iloc[:5]
        == np.array([0.0000, 1662.5757, np.nan, np.nan, np.nan])
    ).all()
    assert(
        data["RECTYPE"].iloc[:5]
        == np.array(["H", "H", "P", "P", "P"])
    ).all()
    assert(
        data["PERNUM"].iloc[:5]
        == np.array([pd.NA, pd.NA, 1, 2, 3]).all()
    )
    assert (data.dtypes.values == np.array([str, pd.Int64Dtype(), pd.Int64Dtype(), pd.Int64Dtype(),
                                            float, pd.Int64Dtype(), pd.Int64Dtype(), pd.Int64Dtype(),
                                            pd.Int64Dtype(), float, pd.Int64Dtype(), pd.Int64Dtype(),
                                            pd.Int64Dtype(), pd.Int64Dtype()])).all()


def _assert_cps_00421_dict(data: Dict):
    """Run all the checks for the data frame returned by our readers for hierarchical files
    when a dictionary of data frames is requested"""
    p_data = data["P"]
    h_data = data["H"]

    assert len(data.keys()) == 2

    assert len(p_data) == 201993
    assert len(p_data.columns) == 9
    assert (p_data["YEAR"].iloc[:5] == 2022).all()
    assert (
        p_data["WTFINL"].iloc[:5]
        == np.array([1662.5757, 1978.19857, 1801.0842, 1243.6042, 2037.9611])
    ).all()
    assert(
        p_data["RECTYPE"].iloc[:5]
        == np.array(["P", "P", "P", "P", "P"])
    ).all()
    assert(
        p_data["PERNUM"].iloc[:5]
        == np.array([1, 2, 3, 4, 1]).all()
    )
    assert (p_data.dtypes.values == np.array([str, pd.Int64Dtype(), pd.Int64Dtype(), pd.Int64Dtype(), float,
                                              pd.Int64Dtype(), pd.Int64Dtype(), pd.Int64Dtype(), pd.Int64Dtype()])).all()

    assert len(h_data) == 137285
    assert len(h_data.columns) == 8
    assert (h_data["YEAR"].iloc[:5] == 2022).all()
    assert (
        p_data["HWTFINL"].iloc[:5]
        == np.array([0.0000, 1662.5757, 2037.9611, 2094.5077, 1970.8250])
    ).all()
    assert(
        p_data["RECTYPE"].iloc[:5]
        == np.array(["H", "H", "H", "H", "H"])
    ).all()
    assert(
        p_data["MISH"].iloc[:5]
        == np.array([7, 5, 1, 2, 1]).all()
    )
    assert (p_data.dtypes.values == np.array([str, pd.Int64Dtype(), pd.Int64Dtype(), pd.Int64Dtype(),
                                              pd.Int64Dtype(), float, pd.Int64Dtype(), pd.Int64Dtype(), 
                                              pd.Int64Dtype()])).all()


def test_can_read_herarchical_df_dat_gz(fixtures_path: Path):
    """
    Confirm that we can read hierarchical microdata ino a single data frame 
    in .dat format when it is gzipped
    """
    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00421.xml")
    data = readers.read_hierarchical_microdata(ddi, fixtures_path / "cps_00421.dat.gz")

    _assert_cps_00421_df


def test_can_read_herarchical_dict_dat_gz(fixtures_path: Path):
    """
    Confirm that we can read hierarchical microdata ino a dictionary of data frames 
    in .dat format when it is gzipped
    """
    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00421.xml")
    data = readers.read_hierarchical_microdata(ddi, fixtures_path / "cps_00421.dat.gz", as_dict=True)

    _assert_cps_00421_dict


def test_can_read_rectangular_dat_gz(fixtures_path: Path):
    """
    Confirm that we can read rectangular microdata in .dat format
    when it is gzipped
    """
    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00006.xml")
    data = readers.read_microdata(ddi, fixtures_path / "cps_00006.dat.gz")

    _assert_cps_000006(data)


def test_can_read_rectangular_csv_gz(fixtures_path: Path):
    """
    Confirm that we can read rectangular microdata in .csv format
    when it is gzipped
    """
    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00006.xml")
    data = readers.read_microdata(ddi, fixtures_path / "cps_00006.csv.gz")

    _assert_cps_000006(data)


def test_can_read_rectangular_dat(fixtures_path: Path):
    """
    Confirm that we can read rectangular microdata in .dat format
    when it is not gzipped
    """
    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00006.xml")

    ## Un gzip the file in our fixtures
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        with gzip.open(fixtures_path / "cps_00006.dat.gz", "rb") as infile:
            with open(tmpdir / "cps_00006.dat", "wb") as outfile:
                for chunk in iter(partial(infile.read, 8192), b""):
                    outfile.write(chunk)

        data = readers.read_microdata(ddi, tmpdir / "cps_00006.dat")

    _assert_cps_000006(data)


def test_can_read_rectangular_parquet(fixtures_path: Path):
    """
    Confirm that we can read rectangular microdata in .parquet format
    """
    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00006.xml")
    data = readers.read_microdata(ddi, fixtures_path / "cps_00006.parquet")

    _assert_cps_000006(data)


@pytest.mark.slow
def test_can_read_rectangular_dat_gz_chunked(fixtures_path: Path):
    """
    Confirm that we can read rectangular microdata in .dat format when chunked
    """
    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00006.xml")
    data = readers.read_microdata_chunked(
        ddi, fixtures_path / "cps_00006.dat.gz", chunksize=1
    )

    total_length = 0
    seen = 0
    first_hwtsupp = np.array([1475.59, 1475.59, 1475.59, 1597.61, 1706.65])
    for df in data:
        total_length += len(df)
        assert len(df.columns) == 8
        if seen < 5:
            assert (df["YEAR"].loc[: 5 - seen] == 1962).all()
            assert (
                df["HWTSUPP"].iloc[: 5 - seen]
                == first_hwtsupp[seen : min(len(df) + seen, 5)]
            ).all()
            seen += len(df)
    assert total_length == 7668


def test_read_microdata_custom_dtype(fixtures_path):
    """
    Make sure use can choose custom dtype in microdata reader.
    """
    # Checking default behaviour
    pandas_types = {
        "YEAR": pd.Int64Dtype(),
        "SERIAL": pd.Int64Dtype(),
        "MONTH": pd.Int64Dtype(),
        "HWTFINL": np.float64,
        "CPSID": pd.Int64Dtype(),
        "ASECFLAG": pd.Int64Dtype(),
        "STATEFIP": pd.Int64Dtype(),
        "HRSERSUF": pd.StringDtype(),
        "PERNUM": pd.Int64Dtype(),
        "WTFINL": np.float64,
        "CPSIDP": pd.Int64Dtype(),
        "AGE": pd.Int64Dtype(),
    }

    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00361.xml")
    data = readers.read_microdata(ddi, fixtures_path / "cps_00361.dat.gz")
    assert data.dtypes.to_dict() == pandas_types

    # custom dtype
    pandas_types_efficient = {
        "YEAR": np.float64,
        "SERIAL": np.float64,
        "MONTH": np.float64,
        "HWTFINL": np.float64,
        "CPSID": np.float64,
        "ASECFLAG": np.float64,
        "STATEFIP": np.float64,
        "HRSERSUF": pd.StringDtype(storage="pyarrow"),
        "PERNUM": np.float64,
        "WTFINL": np.float64,
        "CPSIDP": np.float64,
        "AGE": np.float64,
    }

    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00361.xml")
    dtype = ddi.get_all_types(type_format="pandas_type_efficient", string_pyarrow=True)
    data = readers.read_microdata(ddi, fixtures_path / "cps_00361.dat.gz", dtype=dtype)
    assert data.dtypes.to_dict() == pandas_types_efficient

    with pytest.raises(ValueError):
        # should raise Value when parquet and dtype != None
        readers.read_microdata(ddi, fixtures_path / "cps_00006.parquet", dtype=dtype)


def test_read_microdata_chunked_custom_dtype(fixtures_path):
    """
    Make sure use can choose custom dtype in microdata reader.
    """
    # Checking default behaviour
    pandas_types = {
        "YEAR": pd.Int64Dtype(),
        "SERIAL": pd.Int64Dtype(),
        "MONTH": pd.Int64Dtype(),
        "HWTFINL": np.float64,
        "CPSID": pd.Int64Dtype(),
        "ASECFLAG": pd.Int64Dtype(),
        "STATEFIP": pd.Int64Dtype(),
        "HRSERSUF": pd.StringDtype(),
        "PERNUM": pd.Int64Dtype(),
        "WTFINL": np.float64,
        "CPSIDP": pd.Int64Dtype(),
        "AGE": pd.Int64Dtype(),
    }

    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00361.xml")
    data = readers.read_microdata_chunked(ddi, fixtures_path / "cps_00361.dat.gz")
    assert next(data).dtypes.to_dict() == pandas_types

    # custom dtype
    pandas_types_efficient = {
        "YEAR": np.float64,
        "SERIAL": np.float64,
        "MONTH": np.float64,
        "HWTFINL": np.float64,
        "CPSID": np.float64,
        "ASECFLAG": np.float64,
        "STATEFIP": np.float64,
        "HRSERSUF": pd.StringDtype(storage="pyarrow"),
        "PERNUM": np.float64,
        "WTFINL": np.float64,
        "CPSIDP": np.float64,
        "AGE": np.float64,
    }

    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00361.xml")
    dtype = ddi.get_all_types(type_format="pandas_type_efficient", string_pyarrow=True)
    data = readers.read_microdata_chunked(
        ddi, fixtures_path / "cps_00361.dat.gz", dtype=dtype
    )
    assert next(data).dtypes.to_dict() == pandas_types_efficient

    with pytest.raises(ValueError):
        # should raise Value when parquet and dtype != None
        next(
            readers.read_microdata_chunked(
                ddi, fixtures_path / "cps_00006.parquet", dtype=dtype
            )
        )


def test_read_extract_description(fixtures_path: Path):
    """
    Make sure that equivalent extracts can be read as either json or yaml and that
    if a badly formatted extract is provided, we raise a ValueError
    """
    yaml_extract = readers.read_extract_description(
        fixtures_path / "example_extract.yml"
    )
    json_extract = readers.read_extract_description(
        fixtures_path / "example_extract.json"
    )
    from_api_extract = readers.read_extract_description(
        fixtures_path / "example_extract_from_api.json"
    )

    # Make sure they are the same
    assert yaml_extract == json_extract

    # Make sure the contents are correct
    assert yaml_extract == {
        "extracts": [
            {
                "description": "Simple IPUMS extract",
                "collection": "usa",
                "api_version": "beta",
                "samples": ["us2012b"],
                "variables": ["AGE", "SEX", "RACE"],
                "data_structure": "rectangular",
                "data_format": "fixed_width",
            }
        ],
    }

    extract_description = yaml_extract["extracts"][0]
    extract = BaseExtract._collection_to_extract[extract_description["collection"]](
        **extract_description
    )

    extract_description = from_api_extract["extracts"][0]
    api_extract = BaseExtract._collection_to_extract[extract_description["collection"]](
        **extract_description
    )

    assert isinstance(extract, UsaExtract)
    assert isinstance(api_extract, UsaExtract)

    assert extract.build() == api_extract.build()

    # Check that something that is neither YAML nor JSON yields a ValueError
    with pytest.raises(ValueError):
        readers.read_extract_description(fixtures_path / "cps_00006.xml")
