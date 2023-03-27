import os
import pickle
import subprocess
import time
import yaml
import json
import pickle
import tempfile
from pathlib import Path

import pytest
import vcr

from ipumspy import api, readers
from ipumspy.api import (
    IpumsApiClient,
    OtherExtract,
    UsaExtract,
    CpsExtract,
    extract_from_dict,
    extract_to_dict,
    define_extract_from_ddi,
    define_extract_from_json,
    save_extract_as_json,
    Variable,
    Sample,
)
from ipumspy.api.exceptions import (
    BadIpumsApiRequest,
    IpumsApiException,
    IpumsExtractNotSubmitted,
    IpumsNotFound,
)


@pytest.fixture(scope="function")
def tmpdir() -> Path:
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


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
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"us2012b": {}},
        "variables": {
            "AGE": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "SEX": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
        },
        "description": "My IPUMS USA extract",
        "dataFormat": "fixed_width",
        "collection": "usa",
        "version": None,
    }


def test_usa_attach_characteristics():
    """
    Confirm that attach_characteristics updates extract definition correctly
    """
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
    )
    extract.attach_characteristics("AGE", ["father"])
    assert extract.build() == {
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"us2012b": {}},
        "variables": {
            "AGE": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": ["father"],
                "dataQualityFlags": False,
            },
            "SEX": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
        },
        "description": "My IPUMS USA extract",
        "dataFormat": "fixed_width",
        "collection": "usa",
        "version": None,
    }

    # try to attach characteristics to a not-included variable
    with pytest.raises(ValueError) as exc_info:
        extract.attach_characteristics("RACE", ["father"])
    assert exc_info.value.args[0] == "RACE is not part of this extract."


def test_usa_add_data_quality_flags():
    """
    Confirm that attach_characteristics updates extract definition correctly
    """
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
    )
    extract.add_data_quality_flags("SEX")
    assert extract.build() == {
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"us2012b": {}},
        "variables": {
            "AGE": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "SEX": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": True,
            },
        },
        "description": "My IPUMS USA extract",
        "dataFormat": "fixed_width",
        "collection": "usa",
        "version": None,
    }


def test_usa_select_cases():
    """
    Confirm that attach_characteristics updates extract definition correctly
    """
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "RACE"],
    )
    # general codes
    extract.select_cases("RACE", ["1"], general=True)
    assert extract.build() == {
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"us2012b": {}},
        "variables": {
            "AGE": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "RACE": {
                "preselected": False,
                "caseSelections": {"general": ["1"]},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
        },
        "description": "My IPUMS USA extract",
        "dataFormat": "fixed_width",
        "collection": "usa",
        "version": None,
    }
    # detailed codes
    extract.select_cases("RACE", ["100"], general=False)
    assert extract.build() == {
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"us2012b": {}},
        "variables": {
            "AGE": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "RACE": {
                "preselected": False,
                "caseSelections": {"detailed": ["100"]},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
        },
        "description": "My IPUMS USA extract",
        "dataFormat": "fixed_width",
        "collection": "usa",
        "version": None,
    }


@pytest.mark.vcr
def test_usa_feature_errors(live_api_client: IpumsApiClient):
    """
    Confirm that illegal feature requests raise appropriate errors
    """
    # select an invalid value with the correct level of detail
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX", "RACE"],
    )

    extract.select_cases("AGE", ["200"], general=True)
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(extract)
    assert (
        exc_info.value.args[0]
        == "Invalid general case selection of 200 for variable AGE"
    )
    # ask for detailed codes when  none are available
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX", "RACE"],
    )
    extract.select_cases("SEX", ["100"], general=False)
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(extract)
    assert (
        exc_info.value.args[0]
        == "Detailed case selection made but detailed variable not found for SEX."
    )
    # Specify general codes when requesting detailed codes
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX", "RACE"],
    )
    extract.select_cases("RACE", ["1"], general=False)
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(extract)
    assert (
        exc_info.value.args[0]
        == "Invalid detailed case selection of 001 for variable RACE"
    )


def test_cps_build_extract():
    """
    Confirm that test extract formatted correctly
    """
    extract = CpsExtract(
        ["cps2012_03b"],
        ["AGE", "SEX"],
    )
    assert extract.collection == "cps"
    assert extract.build() == {
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"cps2012_03b": {}},
        "variables": {
            "AGE": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "SEX": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
        },
        "description": "My IPUMS CPS extract",
        "dataFormat": "fixed_width",
        "collection": "cps",
        "version": None,
    }


def test_cps_hierarchical_build_extract():
    """
    Confirm that test extract formatted correctly when hierarchical structure specified
    """
    extract = CpsExtract(
        ["cps2012_03b"], ["AGE", "SEX"], data_structure={"hierarchical": {}}
    )
    assert extract.data_structure == {"hierarchical": {}}


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
    assert len(previous10["usa"]) == 10


@pytest.mark.vcr
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

    # specify "on" w/ hierarchical structure
    bad_structure = UsaExtract(
        ["us2012b"], ["AGE"], data_structure={"hierarchical": {"on": "P"}}
    )
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(bad_structure)
    assert exc_info.value.args[0] == (
        "The property '#/dataStructure/hierarchical' contains additional "
        'properties ["on"] outside of the schema when none are allowed.'
    )

    # specify illegal rectype to rectangularize on
    bad_rectype = UsaExtract(
        ["us2012b"], ["AGE"], data_structure={"rectangular": {"on": "Z"}}
    )
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(bad_rectype)
    assert (
        exc_info.value.args[0]
        == 'Invalid Record Type specified in "data_structure.rectangular.on".'
    )


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


@pytest.mark.vcr
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


@pytest.mark.vcr
def test_not_submitted_exception():
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
    )
    with pytest.raises(IpumsExtractNotSubmitted) as exc_info:
        dct = extract_to_dict(extract)
    assert exc_info.value.args[0] == (
        "Extract has not been submitted and so has no json response"
    )


@pytest.mark.vcr
def test_extract_was_purged(live_api_client: IpumsApiClient):
    """
    test extract_was_purged() method
    """
    was_purged = live_api_client.extract_was_purged(extract="1", collection="usa")
    assert was_purged == True


def test_extract_from_dict(fixtures_path: Path):
    """Ensure extract object can be created from a dict"""
    with open(fixtures_path / "example_extract_v2.yml") as infile:
        extract = extract_from_dict(yaml.safe_load(infile))

    for item in extract:
        assert item.collection == "usa"
        assert item.samples == [Sample(id="us2012b")]
        assert item.variables == [
            Variable(
                name="AGE",
                preselected=False,
                case_selections={},
                attached_characteristics=[],
                data_quality_flags=False,
            ),
            Variable(
                name="SEX",
                preselected=False,
                case_selections={},
                attached_characteristics=[],
                data_quality_flags=False,
            ),
            Variable(
                name="RACE",
                preselected=False,
                case_selections={},
                attached_characteristics=[],
                data_quality_flags=False,
            ),
        ]
        # data structure not currently an extract attribute...
        # assert item.data_structure == "rectangular"
        assert item.data_format == "fixed_width"
        assert item.api_version == 2

    # if an unsupported api version is specified
    # make sure NotImplementedError is raised
    with pytest.raises(NotImplementedError) as exc_info:
        with open(fixtures_path / "example_extract.yml") as infile:
            extract = extract_from_dict(yaml.safe_load(infile))
    assert exc_info.value.args[0] == (
        "The IPUMS API version specified in the extract definition is not supported by this version of ipumspy."
    )


def test_extract_to_dict(fixtures_path: Path):
    # reconstitute the extract object from pickle
    with open(fixtures_path / "usa_00196_extract_obj.pkl", "rb") as infile:
        extract = pickle.load(infile)

    # export extract to dict
    dct = extract_to_dict(extract)
    assert dct["extractDefinition"]["collection"] == "usa"
    assert dct["extractDefinition"]["samples"] == {"us2012b": {}}
    assert dct["extractDefinition"]["variables"] == {
        "YEAR": {"preselected": True},
        "SAMPLE": {"preselected": True},
        "SERIAL": {"preselected": True},
        "CBSERIAL": {"preselected": True},
        "GQ": {"preselected": True},
        "HHWT": {"preselected": True},
        "PERNUM": {"preselected": True},
        "PERWT": {"preselected": True},
        "AGE": {},
        "SEX": {},
    }


@pytest.mark.vcr
def test_submit_extract_live(live_api_client: IpumsApiClient):
    """
    Confirm that test extract submits properly
    """
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
    )

    live_api_client.submit_extract(extract)
    assert live_api_client.extract_status(extract) == "queued"


@pytest.mark.vcr
def test_submit_hierarchical_extract_live(live_api_client: IpumsApiClient):
    """
    Confirm that test extract submits properly
    """
    extract = UsaExtract(
        ["us2012b"], ["AGE", "SEX"], data_structure={"hierarchical": {}}
    )

    live_api_client.submit_extract(extract)
    assert live_api_client.extract_status(extract) == "queued"


@pytest.mark.vcr
def test_download_extract(live_api_client: IpumsApiClient, tmpdir: Path):
    """
    Confirm that extract data and attendant files can be downloaded
    """
    live_api_client.download_extract(
        collection="usa", extract="196", download_dir=tmpdir
    )
    assert (tmpdir / "usa_00196.dat.gz").exists()
    assert (tmpdir / "usa_00196.xml").exists()


@pytest.mark.vcr
def test_download_extract_stata(live_api_client: IpumsApiClient, tmpdir: Path):
    """
    Confirm that extract data and attendant files (Stata) can be downloaded
    """
    live_api_client.download_extract(
        collection="usa", extract="196", stata_command_file=True, download_dir=tmpdir
    )
    assert (tmpdir / "usa_00196.do").exists()


@pytest.mark.vcr
def test_download_extract_spss(live_api_client: IpumsApiClient, tmpdir: Path):
    """
    Confirm that extract data and attendant files (SPSS) can be downloaded
    """
    live_api_client.download_extract(
        collection="usa", extract="196", spss_command_file=True, download_dir=tmpdir
    )
    assert (tmpdir / "usa_00196.sps").exists()


@pytest.mark.vcr
def test_download_extract_sas(live_api_client: IpumsApiClient, tmpdir: Path):
    """
    Confirm that extract data and attendant files (SAS) can be downloaded
    """
    live_api_client.download_extract(
        collection="usa", extract="196", sas_command_file=True, download_dir=tmpdir
    )
    assert (tmpdir / "usa_00196.sas").exists()


@pytest.mark.vcr
def test_download_extract_r(live_api_client: IpumsApiClient, tmpdir: Path):
    """
    Confirm that extract data and attendant files (R) can be downloaded
    """
    live_api_client.download_extract(
        collection="usa", extract="196", r_command_file=True, download_dir=tmpdir
    )
    assert (tmpdir / "usa_00196.R").exists()


def test_define_extract_from_ddi(fixtures_path: Path):
    ddi_codebook = readers.read_ipums_ddi(fixtures_path / "usa_00196.xml")
    extract = define_extract_from_ddi(ddi_codebook)

    assert extract.collection == "usa"
    assert extract.samples == [Sample(id="us2012b")]
    assert extract.variables == [
        Variable(
            name="YEAR",
            preselected=False,
            case_selections={},
            attached_characteristics=[],
            data_quality_flags=False,
        ),
        Variable(
            name="SAMPLE",
            preselected=False,
            case_selections={},
            attached_characteristics=[],
            data_quality_flags=False,
        ),
        Variable(
            name="SERIAL",
            preselected=False,
            case_selections={},
            attached_characteristics=[],
            data_quality_flags=False,
        ),
        Variable(
            name="CBSERIAL",
            preselected=False,
            case_selections={},
            attached_characteristics=[],
            data_quality_flags=False,
        ),
        Variable(
            name="HHWT",
            preselected=False,
            case_selections={},
            attached_characteristics=[],
            data_quality_flags=False,
        ),
        Variable(
            name="GQ",
            preselected=False,
            case_selections={},
            attached_characteristics=[],
            data_quality_flags=False,
        ),
        Variable(
            name="PERNUM",
            preselected=False,
            case_selections={},
            attached_characteristics=[],
            data_quality_flags=False,
        ),
        Variable(
            name="PERWT",
            preselected=False,
            case_selections={},
            attached_characteristics=[],
            data_quality_flags=False,
        ),
        Variable(
            name="SEX",
            preselected=False,
            case_selections={},
            attached_characteristics=[],
            data_quality_flags=False,
        ),
        Variable(
            name="AGE",
            preselected=False,
            case_selections={},
            attached_characteristics=[],
            data_quality_flags=False,
        ),
    ]
    assert extract.data_format == "fixed_width"
    assert extract.api_version == None


def test_define_extract_from_json(fixtures_path: Path):
    """Ensure extract can be created from json file"""
    extract = define_extract_from_json(fixtures_path / "example_extract_v2.json")
    for item in extract:
        assert item.collection == "usa"
        assert item.samples == [Sample(id="us2012b")]
        assert item.variables == [
            Variable(
                name="AGE",
                preselected=False,
                case_selections={},
                attached_characteristics=[],
                data_quality_flags=False,
            ),
            Variable(
                name="SEX",
                preselected=False,
                case_selections={},
                attached_characteristics=[],
                data_quality_flags=False,
            ),
            Variable(
                name="RACE",
                preselected=False,
                case_selections={},
                attached_characteristics=[],
                data_quality_flags=False,
            ),
        ]
        assert item.api_version == 2

    # if an unsupported api version is specified, make sure
    # NotImplementedError is raised
    with pytest.raises(NotImplementedError) as exc_info:
        extract = define_extract_from_json(fixtures_path / "example_extract.json")
    assert exc_info.value.args[0] == (
        "The IPUMS API version specified in the extract definition is not supported by this version of ipumspy."
    )


def test_save_extract_as_json(fixtures_path: Path):
    # remove the test saved extract if it exists
    if Path(fixtures_path / "test_saved_extract.json").exists():
        os.remove(str(Path(fixtures_path / "test_saved_extract.json")))

    # reconstitute the extract object from pickle
    with open(fixtures_path / "usa_00196_extract_obj.pkl", "rb") as infile:
        extract = pickle.load(infile)

    # save it as an extract
    save_extract_as_json(extract, fixtures_path / "test_saved_extract.json")

    assert Path(fixtures_path / "test_saved_extract.json").exists()
    os.remove(str(Path(fixtures_path / "test_saved_extract.json")))


def test_variable_update():
    # update an attribute that doesn't exist
    age = Variable("AGE")
    with pytest.raises(KeyError) as exc_info:
        age.update("fake_attribute", "fake_value")
    assert exc_info.value.args[0] == "Variable has no attribute 'fake_attribute'."