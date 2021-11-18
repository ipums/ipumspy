import os
import subprocess
import time

import pytest

from ipumspy import api
from ipumspy.api import IpumsApiClient, OtherExtract, UsaExtract
from ipumspy.api.exceptions import BadIpumsApiRequest, IpumsNotFound, IpumsApiException


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


@pytest.fixture(scope="function")
def live_api_client(environment_variables) -> IpumsApiClient:
    live_client = IpumsApiClient(os.environ.get("IPUMS_API_KEY"))
    return live_client


def test_usa_build_extract():
    """
    Confirm that test extract formatted correctly
    """
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
    )
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


def test_submit_extract_and_wait_for_extract(api_client: IpumsApiClient):
    """
    Confirm that test extract submits properly
    """
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
    )

    api_client.submit_extract(extract)
    assert extract.extract_id == 10

    api_client.wait_for_extract(extract)
    assert api_client.extract_status(extract) == "completed"


def test_retrieve_previous_extracts(api_client: IpumsApiClient):
    previous10 = api_client.retrieve_previous_extracts("usa")
    # this passes, but needs to be updated to reflect retrieve_previous_extracts updates
    assert len(previous10["usa"]) == 10


@pytest.mark.integration
def test_bad_api_request_exception(live_api_client: IpumsApiClient):
    """
    Confirm that malformed or impossible extract requests raise
    BadIpumsApiRequest exception
    """
    # bad variable
    bad_variable = UsaExtract(["us2012b"], ["AG"])
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(bad_variable)
    assert exc_info.value.args[0] == "Invalid variable name: AG"

    # unavailable variable
    unavailable_variable = UsaExtract(["us2012b"], ["YRIMMIG"])
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(unavailable_variable)
    assert exc_info.value.args[0] == (
        "YRIMMIG: This variable is not available in any "
        "of the samples currently selected."
    )

    # bad sample
    bad_sample = UsaExtract(["us2012x"], ["AGE"])
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(bad_sample)
    assert exc_info.value.args[0] == "Invalid sample name: us2012x"


def test_not_found_exception_mock(api_client: IpumsApiClient):
    """
    Confirm that attempts to check on non-existent extracts raises
    IpumsNotFound exception (using mocks)
    """
    status = api_client.extract_status(extract=0, collection="usa")
    assert status == "not found"

    with pytest.raises(IpumsNotFound) as exc_info:
        api_client.download_extract(extract=0, collection="usa")
    assert exc_info.value.args[0] == (
        "There is no IPUMS extract with extract number "
        "0 in collection usa. "
        "Be sure to submit your extract before trying to download it!"
    )


@pytest.mark.integration
def test_not_found_exception(live_api_client: IpumsApiClient):
    """
    Confirm that attempts to check on non-existent extracts raises
    IpumsNotFound exception
    """
    status = live_api_client.extract_status(extract="0", collection="usa")
    assert status == "not found"

    with pytest.raises(IpumsNotFound) as exc_info:
        live_api_client.download_extract(extract="0", collection="usa")
    assert exc_info.value.args[0] == (
        "There is no IPUMS extract with extract number "
        "0 in collection usa. "
        "Be sure to submit your extract before trying to download it!"
    )

    with pytest.raises(IpumsNotFound) as exc_info:
        live_api_client.resubmit_purged_extract(extract="0", collection="usa")
    assert exc_info.value.args[0] == (
        "Page not found. Perhaps you passed the wrong extract id?"
    )


@pytest.mark.integration
def test_extract_was_purged(live_api_client: IpumsApiClient):
    """
    test extract_was_purged() method
    """
    was_purged = live_api_client.extract_was_purged(extract="1", collection="usa")
    assert was_purged == True
