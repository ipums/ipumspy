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


def test_ddi_codebook(cps_ddi: ddi.Codebook):
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
