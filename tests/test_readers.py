# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

import gzip
import tempfile
from functools import partial
from os import read
from pathlib import Path

import numpy as np
import pytest

from ipumspy import readers
from ipumspy.api.extract import BaseExtract, UsaExtract


def test_can_read_rectangular_dat_gz(fixtures_path: Path):
    """
    Confirm that we can read rectangular microdata in .dat format
    when it is gzipped
    """
    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00006.xml")
    data = readers.read_microdata(ddi, fixtures_path / "cps_00006.dat.gz")

    assert len(data) == 7668
    assert len(data.columns) == 8
    assert (data["YEAR"].iloc[:5] == 1962).all()
    assert (
        data["HWTSUPP"].iloc[:5]
        == np.array([1475.59, 1475.59, 1475.59, 1597.61, 1706.65])
    ).all()


def test_can_read_rectangular_csv_gz(fixtures_path: Path):
    """
    Confirm that we can read rectangular microdata in .csv format
    when it is gzipped
    """
    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00006.xml")
    data = readers.read_microdata(ddi, fixtures_path / "cps_00006.csv.gz")

    assert len(data) == 7668
    assert len(data.columns) == 8
    assert (data["YEAR"].iloc[:5] == 1962).all()
    assert (
        data["HWTSUPP"].iloc[:5]
        == np.array([1475.59, 1475.59, 1475.59, 1597.61, 1706.65])
    ).all()


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

    assert len(data) == 7668
    assert len(data.columns) == 8
    assert (data["YEAR"].iloc[:5] == 1962).all()
    assert (
        data["HWTSUPP"].iloc[:5]
        == np.array([1475.59, 1475.59, 1475.59, 1597.61, 1706.65])
    ).all()


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
        "api_version": "v1",
        "extracts": [
            {
                "description": "Simple IPUMS extract",
                "collection": "usa",
                "samples": ["us2012b"],
                "variables": ["AGE", "SEX", "RACE", "UH_SEX_B1"],
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
