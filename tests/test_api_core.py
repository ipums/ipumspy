import os

import pytest

from ipumspy.api import IpumsApi


@pytest.fixture(scope="function")
def api_client(environment_variables) -> IpumsApi:
    return IpumsApi(os.environ.get("IPUMS_API_KEY"))


def test_build_extract(api_client: IpumsApi):
    """
    Confirm that test extract formatted correctly
    """

    extract = api_client.cps._build_body(
        ["cps1976_01s", "cps1976_02b"], ["YEAR", "MISH", "AGE", "RACE", "UH_SEX_B1"],
    )
    assert extract == {
        "data_structure": {"rectangular": {"on": "P"}},
        "samples": {"cps1976_01s": {}, "cps1976_02b": {}},
        "variables": {"YEAR": {}, "MISH": {}, "AGE": {}, "RACE": {}, "UH_SEX_B1": {}},
        "description": "My IPUMS extract",
        "data_format": "fixed_width",
    }


def test_submit_extract(api_client: IpumsApi):
    """
    Confirm that test extract submits properly
    """
    extract, number = api_client.cps.submit_extract(
        ["cps1976_01s", "cps1976_02b"], ["YEAR", "MISH", "AGE", "RACE", "UH_SEX_B1"]
    )
    assert extract.status_code == 200


def test_retrieve_previous_extracts(api_client: IpumsApi):
    previous = api_client.cps.retrieve_previous_extracts()
    assert len(previous) == 10
