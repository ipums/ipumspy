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
    return readers.read_ipums_ddi(fixtures_path / "cps_00361.xml")


@pytest.fixture(scope="function")
def cps_df2(fixtures_path: Path, cps_ddi2: ddi.Codebook) -> pd.DataFrame:
    return readers.read_microdata(cps_ddi2, fixtures_path / "cps_00361.dat.gz")


@pytest.fixture(scope="function")
def cps_ddi_hierarchical(fixtures_path: Path) -> ddi.Codebook:
    return readers.read_ipums_ddi(fixtures_path / "cps_00421.xml")

# not implemented yet
# @pytest.fixture(scope="function")
# def cps_df_hierarchical(fixtures_path: Path, cps_ddi_hierarchical: ddi.Codebook) -> pd.DataFrame:
#     return readers.read_microdata(cps_ddi_hierarchical, fixtures_path / "cps_00421.dat.gz")


def test_get_variable_info_rectangular(cps_ddi: ddi.Codebook):
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

    # does it have the correct rectype
    assert cps_ddi.get_variable_info("year").rectype == ""

    # And does it raise a ValueError if the variable does not exist?
    with pytest.raises(ValueError):
        cps_ddi.get_variable_info("foo")


def test_get_variable_info_hierarchical(cps_ddi_hierarchical: ddi.Codebook):
    # Does it retrieve the appropriate variable?
    assert cps_ddi_hierarchical.get_variable_info("YEAR").id == "YEAR"

    # Even if the name is not UPPERCASE?
    assert cps_ddi_hierarchical.get_variable_info("year").id == "YEAR"

    # does it give the right description
    assert (
        cps_ddi_hierarchical.get_variable_info("year").description
        == "YEAR reports the year in which the survey was conducted.  YEARP is repeated on person records."
    )

    # does it return the name
    assert cps_ddi_hierarchical.get_variable_info("year").name == "YEAR"

    # codes
    assert cps_ddi_hierarchical.get_variable_info("month").codes == {
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

    # does it have the correct rectype
    assert cps_ddi_hierarchical.get_variable_info("year").rectype == "H P"

    # And does it raise a ValueError if the variable does not exist?
    with pytest.raises(ValueError):
        cps_ddi_hierarchical.get_variable_info("foo")


def test_ddi_codebook_rectangular(cps_ddi: ddi.Codebook):
    # sample descriptions/names
    # looks like the test ddi was generated several versions ago
    # and sample <notes> are now formatted differently.
    # assert cps_ddi.samples_description == ["IPUMS-CPS, ASEC 1962",
    #                                       "IPUMS-CPS, ASEC 1963"]

    # doi
    assert cps_ddi.ipums_doi == "DOI:10.18128/D030.V5.0"

    # data format
    assert cps_ddi.file_description.format == "fixed length fields"

    # data structure
    assert cps_ddi.file_description.structure == "rectangular"

    # rectypes
    assert cps_ddi.file_description.rectypes == []

    # rectype idvar
    assert cps_ddi.file_description.rectype_idvar == ""

    # rectype keyvar
    assert cps_ddi.file_description.rectype_keyvar == ""

    # data collection
    assert cps_ddi.ipums_collection == "cps"

    # citation
    assert cps_ddi.ipums_citation == (
        "Publications and research reports based on the "
        "IPUMS-CPS database must cite it appropriately. "
        "The citation should include the following:\n"
        "\n"
        "Sarah Flood, Miriam King, Steven Ruggles, and "
        "J. Robert Warren. Integrated Public Use "
        "Microdata Series, Current Population Survey: "
        "Version 5.0 [dataset]. Minneapolis, MN: "
        "University of Minnesota, 2017. "
        "https://doi.org/10.18128/D030.V5.0\n"
        "\n"
        "The licensing agreement for use of IPUMS-CPS "
        "data requires that users supply us with the "
        "title and full citation for any publications, "
        "research reports, or educational materials "
        "making use of the data or documentation. Please "
        "add your citation to the IPUMS bibliography: "
        "http://bibliography.ipums.org/"
    )

    # terms of use
    assert cps_ddi.ipums_conditions == (
        "Users of IPUMS-CPS data must agree to abide by "
        "the conditions of use. A user's license is "
        "valid for one year and may be renewed.  Users "
        "must agree to the following conditions:\n"
        "\n"
        "(1) No fees may be charged for use or "
        "distribution of the data.  All persons are "
        "granted a limited license to use these data, "
        "but you may not charge a fee for the data if "
        "you distribute it to others.\n"
        "\n"
        "(2) Cite IPUMS appropriately.  For information "
        "on proper citation,  refer to the citation "
        "requirement section of this DDI document.\n"
        "\n"
        "(3) Tell us about any work you do using the "
        "IPUMS.  Publications, research  reports, or "
        "presentations making use of IPUMS-CPS should "
        "be added to our  Bibliography. Continued "
        "funding for the IPUMS depends on our ability "
        "to  show our sponsor agencies that researchers "
        "are using the data for productive  purposes.\n"
        "\n"
        "(4) Use it for GOOD -- never for EVIL."
    )


def test_ddi_codebook_hierarchical(cps_ddi_hierarchical: ddi.Codebook):
    # sample descriptions/names
    assert cps_ddi_hierarchical.samples_description == ["IPUMS-CPS, January 2022",
                                                        "IPUMS-CPS, January 2023"]

    # doi
    assert cps_ddi_hierarchical.ipums_doi == "DOI:10.18128/D030.V10.0"

    # data format
    assert cps_ddi_hierarchical.file_description.format == "fixed length fields"

    # data structure
    assert cps_ddi_hierarchical.file_description.structure == "hierarchical"

    # rectypes
    assert cps_ddi_hierarchical.file_description.rectypes == ["P", "H"]

    # rectype idvar
    assert cps_ddi_hierarchical.file_description.rectype_idvar == "RECTYPE"

    # rectype keyvar
    assert cps_ddi_hierarchical.file_description.rectype_keyvar == "SERIAL"

    # data collection
    assert cps_ddi_hierarchical.ipums_collection == "cps"

    # citation
    assert cps_ddi_hierarchical.ipums_citation == (
        "Publications and research reports based on the "
        "IPUMS-CPS database must cite it appropriately. "
        "The citation should include the following:\n"
        "\n"
        "Sarah Flood, Miriam King, Renae Rodgers, Steven Ruggles, "
        "J. Robert Warren and Michael Westberry. Integrated Public Use "
        "Microdata Series, Current Population Survey: "
        "Version 10.0 [dataset]. Minneapolis, MN: "
        "IPUMS, 2022. "
        "https://doi.org/10.18128/D030.V10.0\n"
        "\n"
        "The licensing agreement for use of IPUMS-CPS "
        "data requires that users supply us with the "
        "title and full citation for any publications, "
        "research reports, or educational materials "
        "making use of the data or documentation. Please "
        "add your citation to the IPUMS bibliography: "
        "http://bibliography.ipums.org/"
    )

    # terms of use
    assert cps_ddi_hierarchical.ipums_conditions == (
        "Users of IPUMS-CPS data must agree to abide by "
        "the conditions of use. A user's license is "
        "valid for one year and may be renewed.  Users "
        "must agree to the following conditions:\n"
        "\n"
        "(1) No fees may be charged for use or "
        "distribution of the data.  All persons are "
        "granted a limited license to use these data, "
        "but you may not charge a fee for the data if "
        "you distribute it to others.\n"
        "\n"
        "(2) Cite IPUMS appropriately.  For information "
        "on proper citation,  refer to the citation "
        "requirement section of this DDI document.\n"
        "\n"
        "(3) Tell us about any work you do using the "
        "IPUMS.  Publications, research  reports, or "
        "presentations making use of IPUMS-CPS should "
        "be added to our  Bibliography. Continued "
        "funding for the IPUMS depends on our ability "
        "to  show our sponsor agencies that researchers "
        "are using the data for productive  purposes.\n"
        "\n"
        "(4) Use it for GOOD -- never for EVIL."
    )


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

    # Does it raise a ValueError if the specified type of format, doesn't match existing attribute?
    with pytest.raises(ValueError):
        cps_ddi.get_all_types(type_format="foo")


def test_get_all_types_with_pyarrow(cps_ddi2: ddi.Codebook, cps_df2: pd.DataFrame):
    pandas_types = {
        "YEAR": pd.Int64Dtype(),
        "SERIAL": pd.Int64Dtype(),
        "MONTH": pd.Int64Dtype(),
        "HWTFINL": np.float64,
        "CPSID": pd.Int64Dtype(),
        "ASECFLAG": pd.Int64Dtype(),
        "STATEFIP": pd.Int64Dtype(),
        "HRSERSUF": pd.StringDtype(storage="pyarrow"),
        "PERNUM": pd.Int64Dtype(),
        "WTFINL": np.float64,
        "CPSIDP": pd.Int64Dtype(),
        "AGE": pd.Int64Dtype(),
    }

    assert (
        cps_ddi2.get_all_types(type_format="pandas_type", string_pyarrow=True)
        == pandas_types
    )

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
