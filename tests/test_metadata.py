import os
import pytest

from ipumspy.api import IpumsApiClient

from ipumspy.api.metadata import (
    NhgisDatasetMetadata,
    NhgisDataTableMetadata,
    IhgisDatasetMetadata,
    IhgisDataTableMetadata,
    TimeSeriesTableMetadata,
)

from ipumspy.api.exceptions import IpumsApiRateLimitException


@pytest.fixture(scope="function")
def live_api_client(environment_variables) -> IpumsApiClient:
    live_client = IpumsApiClient(os.environ.get("IPUMS_API_KEY"))
    return live_client


@pytest.mark.vcr
def test_get_metadata_catalog(live_api_client: IpumsApiClient):
    """
    Test that we can retrieve paginated metadata endpoints from API
    """

    datasets = live_api_client.get_metadata_catalog("nhgis", "datasets", page_size=5)
    samples = live_api_client.get_metadata_catalog("usa", "samples", page_size=5)

    ds = next(datasets)["data"]
    samp = next(samples)["data"]

    assert [d["name"] for d in ds] == [
        "1790_cPop",
        "1800_cPop",
        "1810_cPop",
        "1820_cPop",
        "1830_cPop",
    ]
    assert [s["name"] for s in samp] == [
        "us1850a",
        "us1850c",
        "us1860a",
        "us1860b",
        "us1860c",
    ]
    assert list(ds[0].keys()) == ["name", "group", "description", "sequence"]
    assert list(samp[0].keys()) == ["name", "description"]


@pytest.mark.vcr
def test_get_nhgis_metadata(live_api_client: IpumsApiClient):
    ds = NhgisDatasetMetadata("1990_STF1")
    dt = NhgisDataTableMetadata("B01001", "2017_2021_ACS5a")
    tt = TimeSeriesTableMetadata("nhgis", "CW3")

    ds = live_api_client.get_metadata(ds)
    dt = live_api_client.get_metadata(dt)
    tt = live_api_client.get_metadata(tt)

    assert isinstance(ds, NhgisDatasetMetadata)
    assert isinstance(dt, NhgisDataTableMetadata)
    assert isinstance(tt, TimeSeriesTableMetadata)

    assert ds.description == "STF 1 - 100% Data"
    assert dt.description == "Sex by Age"
    assert tt.description == "Persons by Age [22]"

    assert len(ds.data_tables) == 100
    assert len(dt.variables) == 49
    assert len(tt.time_series) == 22


# TODO: Enable test when IHGIS released to live. Currently only on demo
"""
@pytest.mark.vcr
def test_get_ihgis_metadata(live_api_client: IpumsApiClient):
    ds = IhgisDatasetMetadata("KZ2009pop")
    dt = IhgisDataTableMetadata("KZ2009pop.AAA")

    ds = live_api_client.get_metadata(ds)
    dt = live_api_client.get_metadata(dt)

    assert isinstance(ds, IhgisDatasetMetadata)
    assert isinstance(dt, IhgisDataTableMetadata)

    assert ds.description == "Results of the 2009 National Population Census of the Republic of Kazakhstan"
    assert dt.label == "Urban and rural population"

    assert len(ds.data_tables) == 6
    assert len(dt.variables) == 9
"""


def test_collection_validity():
    with pytest.raises(ValueError) as exc_info:
        ds = TimeSeriesTableMetadata("usa", "CW3")
    assert (
        exc_info.value.args[0]
        == "TimeSeriesTableMetadata is not a valid metadata type for the usa collection."
    )


@pytest.mark.vcr
@pytest.mark.slow
def test_ipums_api_rate_limit_exception(live_api_client: IpumsApiClient):
    with pytest.raises(IpumsApiRateLimitException) as exc_info:
        for page in live_api_client.get_metadata_catalog(
            "nhgis", metadata_type="data_tables", page_size=5
        ):
            for dt in page["data"]:
                continue
    assert exc_info.value.args[0] == "You have exceeded the API rate limit."
