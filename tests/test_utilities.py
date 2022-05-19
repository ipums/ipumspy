# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import vcr

from ipumspy import readers
from ipumspy.utilities import tabulate, CollectionInformation


def test_tabulate(fixtures_path: Path):
    """
    Confirm that tabulate functions as expected
    """
    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00006.xml")
    data = readers.read_microdata(ddi, fixtures_path / "cps_00006.dat.gz")
    year_info = ddi.get_variable_info("YEAR")
    crosstab_df = tabulate(year_info, data)

    assert list(crosstab_df.columns) == ["counts", "pct"]
    assert (crosstab_df["counts"]).all() == (np.array([4065, 3603])).all()
    assert (crosstab_df["pct"]).all() == (np.array([0.530125, 0.469875])).all()

    ddi = readers.read_ipums_ddi(fixtures_path / "cps_00006.xml")
    data = readers.read_microdata(ddi, fixtures_path / "cps_00006.dat.gz")
    month_info = ddi.get_variable_info("MONTH")
    crosstab_df = tabulate(month_info, data)

    assert list(crosstab_df.columns) == ["val", "lab", "counts", "pct"]
    assert (crosstab_df["val"]).all() == (np.array([3])).all()
    assert list(crosstab_df["lab"]) == ["March"]
    assert (crosstab_df["counts"]).all() == (np.array([7668])).all()
    assert (crosstab_df["pct"]).all() == (np.array([1.0])).all()


@pytest.mark.vcr
def test_get_sample_ids():
    sample_ids = CollectionInformation("cps").sample_ids
    assert sample_ids["IPUMS-CPS, ASEC 2019"] == "cps2019_03s"
    assert sample_ids["IPUMS-CPS, January 1976"] == "cps1976_01s"
