import os
import subprocess
import time

import pytest

from ipumspy.api import IpumsApiClient, OtherExtract, UsaExtract


@pytest.fixture(scope="module")
def mock_api() -> str:
    # TODO: Would be good to randomly assign a port and return it
    p = subprocess.Popen(
        ["uvicorn", "tests.mock_api:app", "--host", "127.0.0.1", "--port", "8989"]
    )
    time.sleep(1)  # Give it enough time to warm up
    try:
        yield "http://127.0.0.1:8989/extracts"
    finally:
        p.kill()


@pytest.fixture(scope="function")
def api_client(environment_variables, mock_api: str) -> IpumsApiClient:
    client = IpumsApiClient(os.environ.get("IPUMS_API_KEY"))
    client.base_url = mock_api
    return client


def test_usa_build_extract():
    """
    Confirm that test extract formatted correctly
    """
    extract = UsaExtract(["us2012b"], ["AGE", "SEX"],)
    assert extract.collection == "usa"
    assert extract.build() == {
        "data_structure": {"rectangular": {"on": "P"}},
        "samples": {"us2012b": {}},
        "variables": {"AGE": {}, "SEX": {}},
        "description": "My IPUMS extract",
        "data_format": "fixed_width",
    }


def test_other_build_extract():
    details = {"some": [1, 2, 3], "other": ["a", "b", "c"]}
    extract = OtherExtract("foo", details)
    assert extract.build() == details
    assert extract.collection == "foo"


def test_submit_extract(api_client: IpumsApiClient):
    """
    Confirm that test extract submits properly
    """
    extract = UsaExtract(["us2012b"], ["AGE", "SEX"],)

    api_client.submit_extract(extract)
    assert extract.extract_id == 10


def test_retrieve_previous_extracts(api_client: IpumsApiClient):
    previous = api_client.retrieve_previous_extracts(collection="usa")
    assert "usa" in previous
    assert len(previous["usa"]) == 10

    previous = api_client.retrieve_previous_extracts()
    assert "usa" in previous
    assert len(previous["usa"]) == 10
