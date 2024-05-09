import os
import pickle
import subprocess
import time
import yaml
import json
import pickle
import tempfile
import warnings
from pathlib import Path

import pytest
import vcr

from ipumspy import api, readers
from ipumspy.api import (
    IpumsApiClient,
    MicrodataExtract,
    extract_from_dict,
    extract_to_dict,
    define_extract_from_json,
    save_extract_as_json,
    Variable,
    Sample,
    TimeUseVariable,
)
from ipumspy.api.exceptions import (
    BadIpumsApiRequest,
    IpumsApiException,
    IpumsExtractNotSubmitted,
    IpumsNotFound,
    IpumsExtractNotReady,
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
        yield "http://127.0.0.1:8989"
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
    extract = MicrodataExtract(
        "usa",
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
    extract = MicrodataExtract(
        "usa",
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
    extract = MicrodataExtract(
        "usa",
        ["us2012b"],
        ["AGE", "SEX", "RACE"],
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
            "RACE": {
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

    # add a list of flags
    extract = MicrodataExtract(
        "usa",
        ["us2012b"],
        ["AGE", "SEX", "RACE"],
    )

    extract.add_data_quality_flags(["AGE", "RACE"])
    assert extract.build() == {
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"us2012b": {}},
        "variables": {
            "AGE": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": True,
            },
            "SEX": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "RACE": {
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
    extract = MicrodataExtract(
        "usa",
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
def test_select_cases_feature_errors(live_api_client: IpumsApiClient):
    """
    Confirm that illegal select cases feature requests raise appropriate errors
    """
    # select an invalid value with the correct level of detail
    extract = MicrodataExtract(
        "usa",
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
    extract = MicrodataExtract(
        "usa",
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
    extract = MicrodataExtract(
        "usa",
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


@pytest.mark.vcr
def test_attach_characteristics_feature_errors(live_api_client: IpumsApiClient):
    """
    Confirm that illegal attach characteristics feature requests raise appropriate errors
    """
    # ask for nonexistent pointer from ipumsi
    extract = MicrodataExtract(
        "ipumsi",
        ["am2011a"],
        ["AGE", "SEX"],
    )
    extract.attach_characteristics("AGE", ["father2"])
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(extract)
    assert exc_info.value.args[0] == (
        "Attached variable AGE requested for a same-sex parent, "
        "but attached characteristics support in IPUMS-International "
        "is limited to 'father', 'head', 'mother', and 'spouse'."
    )


def test_cps_build_extract():
    """
    Confirm that test extract formatted correctly
    """
    extract = MicrodataExtract(
        "cps",
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


def test_ipumsi_build_extract():
    """
    Confirm that test extract formatted correctly
    """
    extract = MicrodataExtract(
        "ipumsi",
        ["am2011a"],
        ["AGE", "SEX"],
    )
    assert extract.build() == {
        "description": "My IPUMS IPUMSI extract",
        "dataFormat": "fixed_width",
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"am2011a": {}},
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
        "collection": "ipumsi",
        "version": None,
    }
    

def test_atus_build_extract():
    """
    Confirm that test extract formatted correctly
    """
    extract = MicrodataExtract(
        "atus",
        ["at2016"],
        ["AGE", "SEX"],
        time_use_variables = ["BLS_PCARE"]
    )
    assert extract.build() == {
        "description": "My IPUMS ATUS extract",
        "dataFormat": "fixed_width",
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"at2016": {}},
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
        "timeUseVariables": {
            "BLS_PCARE": {}
        },
        "collection": "atus",
        "version": None,
    }
    
    extract = MicrodataExtract(
        "atus",
        ["at2016"],
        ["AGE", "SEX"],
        time_use_variables = ["BLS_PCARE"],
        sample_members = {"include_non_respondents": True}
    )
    assert extract.build() == {
        "description": "My IPUMS ATUS extract",
        "dataFormat": "fixed_width",
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"at2016": {}},
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
        "timeUseVariables": {
            "BLS_PCARE": {}
        },
        "sampleMembers":{
            "includeNonRespondents": True
        },
        "collection": "atus",
        "version": None,
    }
    
    extract = MicrodataExtract(
        "atus",
        ["at2016"],
        ["AGE", "SEX"],
        time_use_variables = [TimeUseVariable(name="BLS_PCARE"), TimeUseVariable(name="USER_TUV", owner="newuser@gmail.com")],
        sample_members = {"include_non_respondents": True}
    )
    
    assert extract.build() == {
        "description": "My IPUMS ATUS extract",
        "dataFormat": "fixed_width",
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"at2016": {}},
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
        "timeUseVariables": {
            "BLS_PCARE": {},
            "USER_TUV": {"owner": "newuser@gmail.com"}
        },
        "sampleMembers":{
            "includeNonRespondents": True
        },
        "collection": "atus",
        "version": None,
    }
    
    with pytest.raises(TypeError) as exc_info:
        extract = MicrodataExtract(
            "atus",
            ["at2016"],
            ["AGE", "SEX"],
            time_use_variables = ["BLS_PCARE", TimeUseVariable(name="user_TUV", owner="newuser@gmail.com")]
        )
    assert exc_info.value.args[0] == "The items in ['BLS_PCARE', TimeUseVariable(name='user_tuv', owner='newuser@gmail.com')] must all be string type or <class 'ipumspy.api.extract.TimeUseVariable'> type."  

    with pytest.raises(ValueError) as exc_info:
        extract = MicrodataExtract(
            "cps",
            ["cps2016_03b"],
            ["AGE", "SEX"],
            time_use_variables = ["BLS_PCARE"]
        )
        
    assert exc_info.value.args[0] == "Time use variables are unavailable for the IPUMS CPS data collection"
    
    
    

def test_cps_hierarchical_build_extract():
    """
    Confirm that test extract formatted correctly when hierarchical structure specified
    """
    extract = MicrodataExtract(
        "usa", ["cps2012_03b"], ["AGE", "SEX"], data_structure={"hierarchical": {}}
    )
    assert extract.data_structure == {"hierarchical": {}}


# def test_other_build_extract():
#     details = {"some": [1, 2, 3], "other": ["a", "b", "c"]}
#     extract = OtherExtract("foo", details)
#     assert extract.build() == details
#     assert extract.collection == "foo"


def test_submit_extract_and_wait_for_extract(api_client: IpumsApiClient):
    """
    Confirm that test extract submits properly
    """
    extract = MicrodataExtract(
        "usa",
        ["us2012b"],
        ["AGE", "SEX"],
    )

    api_client.submit_extract(extract)
    assert extract.extract_id == 10

    api_client.wait_for_extract(extract)
    assert api_client.extract_status(extract) == "completed"


def test_get_previous_extracts(api_client: IpumsApiClient):
    previous10 = api_client.get_previous_extracts("usa")
    assert len(previous10["usa"]) == 10


@pytest.mark.vcr
def test_bad_api_request_exception(live_api_client: IpumsApiClient):
    """
    Confirm that malformed or impossible extract requests raise
    BadIpumsApiRequest exception
    """
    # bad variable
    bad_variable = MicrodataExtract("usa", ["us2012b"], ["AG"])
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(bad_variable)
    assert exc_info.value.args[0] == "Invalid variable name: AG"

    # unavailable variable
    unavailable_variable = MicrodataExtract("usa", ["us2012b"], ["YRIMMIG"])
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(unavailable_variable)
    assert exc_info.value.args[0] == (
        "YRIMMIG: This variable is not available in any "
        "of the samples currently selected."
    )

    # bad sample
    bad_sample = MicrodataExtract("usa", ["us2012x"], ["AGE"])
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(bad_sample)
    assert exc_info.value.args[0] == "Invalid sample name: us2012x"

    # specify "on" w/ hierarchical structure
    bad_structure = MicrodataExtract(
        "usa", ["us2012b"], ["AGE"], data_structure={"hierarchical": {"on": "P"}}
    )
    with pytest.raises(BadIpumsApiRequest) as exc_info:
        live_api_client.submit_extract(bad_structure)
    assert exc_info.value.args[0] == (
        "The property '#/dataStructure/hierarchical' contains additional "
        'properties ["on"] outside of the schema when none are allowed.'
    )

    # specify illegal rectype to rectangularize on
    bad_rectype = MicrodataExtract(
        "usa", ["us2012b"], ["AGE"], data_structure={"rectangular": {"on": "Z"}}
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


@pytest.mark.vcr
def test_not_submitted_exception():
    extract = MicrodataExtract(
        "usa",
        ["us2012b"],
        ["AGE", "SEX"],
    )
    with pytest.raises(IpumsExtractNotSubmitted) as exc_info:
        dct = extract_to_dict(extract)
    assert exc_info.value.args[0] == (
        "Extract has not been submitted and so has no json response"
    )


@pytest.mark.vcr
def test_extract_is_expired(live_api_client: IpumsApiClient):
    """
    Ensure expired status is correctly returned
    """
    is_expired = live_api_client.extract_is_expired(extract="1", collection="usa")
    assert is_expired == True


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


    with open(fixtures_path / "example_extract_v2_complex.yml") as infile:
        extract = extract_from_dict(yaml.safe_load(infile))

    for item in extract:
        assert item.collection == "usa"
        assert item.samples == [Sample(id="us2012b")]
        assert item.variables == [
            Variable(
                name="AGE",
                preselected=False,
                case_selections={},
                attached_characteristics=["mother"],
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
    assert dct["collection"] == "usa"
    assert dct["samples"] == {"us2012b": {}}
    assert dct["variables"] == {
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
    extract = MicrodataExtract(
        "usa",
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
    extract = MicrodataExtract(
        "usa", ["us2012b"], ["AGE", "SEX"], data_structure={"hierarchical": {}}
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
def test_download_expired_extract(live_api_client: IpumsApiClient, tmpdir: Path):
    # if the extract has expired, raise IpumsExtractNotReady error
    with pytest.raises(IpumsExtractNotReady) as exc_info:
        live_api_client.download_extract(
            collection="usa", extract="1", download_dir=tmpdir
        )
    assert exc_info.value.args[0] == (
        "IPUMS usa extract 1 has expired and its files have been deleted.\n"
        "Use `get_extract_by_id()` and `submit_extract()` to resubmit this definition as a new extract request."
    )


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
        
    extract = define_extract_from_json(fixtures_path / "example_extract_v2_complex.json")
    for item in extract:
        assert item.collection == "usa"
        assert item.samples == [Sample(id="us2012b")]
        assert item.variables == [
            Variable(
                name="AGE",
                preselected=False,
                case_selections={},
                attached_characteristics=["mother"],
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


def test_extract_from_api_response_json(fixtures_path: Path):
    """
    Ensure extract object can be created from a dict that contains
    variable-level features as nested dicts
    """
    extract = define_extract_from_json(
        fixtures_path / "example_fancy_extract_from_api_v2.json"
    )
    for item in extract:
        assert item.collection == "usa"
        assert item.samples == [Sample(id="us2012b")]
        assert item.variables == [
            Variable(
                name="YEAR",
                preselected=True,
                case_selections={},
                attached_characteristics=[],
                data_quality_flags=False,
            ),
            Variable(
                name="AGE",
                preselected=False,
                case_selections={"general": [1, 2, 3]},
                attached_characteristics=[],
                data_quality_flags=False,
            ),
            Variable(
                name="SEX",
                preselected=False,
                case_selections={},
                attached_characteristics=[],
                data_quality_flags=True,
            ),
            Variable(
                name="RACE",
                preselected=False,
                case_selections={},
                attached_characteristics=[
                    "head",
                    "mother",
                    "mother2",
                    "father",
                    "father2",
                    "spouse",
                ],
                data_quality_flags=False,
            ),
        ]
        assert item.api_version == 2


def test_tuv_extract_from_api_response_json(fixtures_path: Path):
    """
    Ensure extract object can be created from a dict that contains
    variable-level and time use variable features as nested dicts
    """
    extract = define_extract_from_json(
        fixtures_path / "example_tuv_extract_v2.json"
    )
    
    assert extract.collection == "atus"
    assert extract.time_use_variables == [
        TimeUseVariable(name = "BLS_PCARE")
    ]
    assert extract.kwargs["sampleMembers"] == {
        "includeHouseholdMembers": False, 
        "includeNonRespondents": True
    }
    assert extract.build()["sampleMembers"] == {
        "includeHouseholdMembers": False, 
        "includeNonRespondents": True
    }


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
    
    
def test_tuv_update():
    tuv = TimeUseVariable("USER_TUV")
    tuv.update("owner", "newuser@gmail.com")
    assert tuv.owner == "newuser@gmail.com"
    


def test_validate_list_args():
    str_extract = MicrodataExtract("ipumsi", ["ar2011a"], ["age", "age", "sex", "sex", "race"])

    assert str_extract.variables == (
        [
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
    )

    with pytest.raises(ValueError) as exc_info:
        vars_extract = MicrodataExtract(
            "ipumsi",
            ["ar2011a"],
            [
                Variable("age", attached_characteristics=["father"]),
                Variable("age"),
                Variable("sex"),
                Variable("sex"),
                Variable("race"),
            ],
        )
    assert (
        exc_info.value.args[0]
        == "Duplicate Variable objects are not allowed in IPUMS Extract definitions."
    )

    str_extract = MicrodataExtract("cps", ["cps2012_03s", "cps2012_03s", "cps2013_03s"], ["AGE"])
    assert str_extract.samples == ([Sample(id="cps2012_03s"), Sample(id="cps2013_03s")])

    with pytest.raises(ValueError) as exc_info:
        samples_extract = MicrodataExtract(
            "cps",
            [
                Sample(id="cps2012_03s"),
                Sample(id="cps2012_03s"),
                Sample(id="cps2013_03s"),
            ],
            ["AGE"],
        )
    assert (
        exc_info.value.args[0]
        == "Duplicate Sample objects are not allowed in IPUMS Extract definitions."
    )
    
    # make sure duplicate objects raise an error    
    with pytest.raises(ValueError) as exc_info:
        obj_extract = MicrodataExtract(
            "cps",
            [
                Sample(id="cps2012_03s"),
                Sample(id="cps2013_03s"),
            ],
            [Variable(name="AGE"), Variable(name="AGE", attached_characteristics=["mother"])],
        )
    assert (
        exc_info.value.args[0]
        == "Duplicate Variable objects are not allowed in IPUMS Extract definitions."
    )
    
    with pytest.raises(TypeError) as exc_info:
        mixed_extract = MicrodataExtract(
            "cps",
            [
                Sample(id="cps2012_03s"),
                Sample(id="cps2013_03s"),
            ],
            [Variable(name="AGE"), "SEX"],
        )
    assert (
        exc_info.value.args[0]
        == "The items in [Variable(name='AGE', preselected=False, case_selections={}, attached_characteristics=[], data_quality_flags=False), 'SEX'] must all be string type or <class 'ipumspy.api.extract.Variable'> type."
    )


@pytest.mark.vcr
def test_get_extract_by_id(live_api_client: IpumsApiClient):
    """
    Make sure extract can be retrieved with specific ID
    """
    cps_ext = live_api_client.get_extract_by_id(433, "cps")
    assert isinstance(cps_ext, MicrodataExtract)
    assert cps_ext.build() == {
        "description": "my extract",
        "dataFormat": "fixed_width",
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"cps2023_01s": {}},
        "variables": {
            "YEAR": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "SERIAL": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "MONTH": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "HWTFINL": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "CPSID": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "PERNUM": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "WTFINL": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "CPSIDP": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
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
            "RACE": {
                "preselected": False,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
        },
        "collection": "cps",
        "version": 2,
    }

    ipumsi_ext = live_api_client.get_extract_by_id(6, "ipumsi")
    assert isinstance(ipumsi_ext, MicrodataExtract)
    assert ipumsi_ext.build() == {
        "description": "My IPUMS International extract",
        "dataFormat": "fixed_width",
        "dataStructure": {"rectangular": {"on": "P"}},
        "samples": {"am2011a": {}},
        "variables": {
            "COUNTRY": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "YEAR": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "SAMPLE": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "SERIAL": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "HHWT": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "PERNUM": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
            "PERWT": {
                "preselected": True,
                "caseSelections": {},
                "attachedCharacteristics": [],
                "dataQualityFlags": False,
            },
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
        "collection": "ipumsi",
        "version": 2,
    }

    # extract with warnings
    with pytest.warns(Warning) as record:
        ext = live_api_client.get_extract_by_id(95, "cps")
        if not record:
            pytest.fail("Expected ModifiedIpumsExtract warning.")


@pytest.mark.vcr
def test_get_all_sample_info(live_api_client: IpumsApiClient):
    """
    Test that all samples are being gotten
    """
    usa_samples = live_api_client.get_all_sample_info("usa")
    assert usa_samples == {
        "us1850a": "1850 1%",
        "us1850c": "1850 100% sample (Revised November 2023)",
        "us1860a": "1860 1%",
        "us1860b": "1860 1% sample with black oversample",
        "us1860c": "1860 100% sample (Revised November 2023)",
        "us1870a": "1870 1%",
        "us1870b": "1870 1% sample with black oversample",
        "us1870c": "1870 100% sample (Revised November 2023)",
        "us1880a": "1880 1%",
        "us1880d": "1880 10%",
        "us1880e": "1880 100% database (Revised November 2023)",
        "us1900k": "1900 1%",
        "us1900j": "1900 5%",
        "us1900l": "1900 1% sample with oversamples",
        "us1900m": "1900 100% database",
        "us1910h": "1910 Puerto Rico",
        "us1910k": "1910 1%",
        "us1910l": "1910 1.4% sample with oversamples",
        "us1910m": "1910 100% database",
        "us1920a": "1920 1%",
        "us1920b": "1920 Puerto Rico sample",
        "us1920c": "1920 100% database",
        "us1930a": "1930 1%",
        "us1930b": "1930 5%",
        "us1930c": "1930 Puerto Rico",
        "us1930d": "1930 100% database",
        "us1940a": "1940 1%",
        "us1940b": "1940 100% database",
        "us1950a": "1950 1%",
        "us1950b": "1950 100% database",
        "us1960a": "1960 1%",
        "us1960b": "1960 5%",
        "us1970a": "1970 Form 1 State",
        "us1970b": "1970 Form 2 State",
        "us1970c": "1970 Form 1 Metro",
        "us1970d": "1970 Form 2 Metro",
        "us1970e": "1970 Form 1 Neighborhood",
        "us1970f": "1970 Form 2 Neighborhood",
        "us1970h": "1970 Puerto Rico State",
        "us1970i": "1970 Puerto Rico Municipio",
        "us1970j": "1970 Puerto Rico Neighborhood",
        "us1980a": "1980 5%",
        "us1980b": "1980 1%",
        "us1980c": "1980 Urban/Rural",
        "us1980d": "1980 Labor Market Area",
        "us1980e": "1980 Detailed metro/non-metro",
        "us1980f": "1980 Puerto Rico 5%",
        "us1980g": "1980 Puerto Rico 1%",
        "us1990a": "1990 5%",
        "us1990b": "1990 1%",
        "us1990c": "1990 Unweighted 1%",
        "us1990d": "1990 Elderly",
        "us1990e": "1990 Labor Market Area",
        "us1990f": "1990 Puerto Rico 5%",
        "us1990g": "1990 Puerto Rico 1%",
        "us2000d": "2000 ACS",
        "us2000b": "2000 1% sample (old version)",
        "us2000c": "2000 Unweighted 1%",
        "us2000a": "2000 5%",
        "us2000e": "2000 Puerto Rico 5%",
        "us2000f": "2000 Puerto Rico 1% sample (old version)",
        "us2000g": "2000 1%",
        "us2000h": "2000 Puerto Rico 1%",
        "us2001a": "2001 ACS",
        "us2002a": "2002 ACS",
        "us2003a": "2003 ACS",
        "us2004a": "2004 ACS",
        "us2005a": "2005 ACS",
        "us2005b": "2005 PRCS",
        "us2006a": "2006 ACS",
        "us2006b": "2006 PRCS",
        "us2007a": "2007 ACS",
        "us2007b": "2007 PRCS",
        "us2007c": "2005-2007, ACS 3-year",
        "us2007d": "2005-2007, PRCS 3-year",
        "us2008a": "2008 ACS",
        "us2008b": "2008 PRCS",
        "us2008c": "2006-2008, ACS 3-year",
        "us2008d": "2006-2008, PRCS 3-year",
        "us2009a": "2009 ACS",
        "us2009b": "2009 PRCS",
        "us2009c": "2007-2009, ACS 3-year",
        "us2009d": "2007-2009, PRCS 3-year",
        "us2009e": "2005-2009, ACS 5-year",
        "us2009f": "2005-2009, PRCS 5-year",
        "us2010a": "2010 ACS",
        "us2010b": "2010 PRCS",
        "us2010c": "2008-2010, ACS 3-year",
        "us2010d": "2008-2010, PRCS 3-year",
        "us2010e": "2006-2010, ACS 5-year",
        "us2010f": "2006-2010, PRCS 5-year",
        "us2010g": "2010 10%",
        "us2010h": "2010 Puerto Rico 10%",
        "us2011a": "2011 ACS",
        "us2011b": "2011 PRCS",
        "us2011c": "2009-2011, ACS 3-year",
        "us2011d": "2009-2011, PRCS 3-year",
        "us2011e": "2007-2011, ACS 5-year",
        "us2011f": "2007-2011, PRCS 5-year",
        "us2012a": "2012 ACS",
        "us2012b": "2012 PRCS",
        "us2012c": "2010-2012, ACS 3-year",
        "us2012d": "2010-2012, PRCS 3-year",
        "us2012e": "2008-2012, ACS 5-year",
        "us2012f": "2008-2012, PRCS 5-year",
        "us2013a": "2013 ACS",
        "us2013b": "2013 PRCS",
        "us2013c": "2011-2013, ACS 3-year",
        "us2013d": "2011-2013, PRCS 3-year",
        "us2013e": "2009-2013, ACS 5-year",
        "us2013f": "2009-2013, PRCS 5-year",
        "us2014a": "2014 ACS",
        "us2014b": "2014 PRCS",
        "us2014c": "2010-2014, ACS 5-year",
        "us2014d": "2010-2014, PRCS 5-year",
        "us2015a": "2015 ACS",
        "us2015b": "2015 PRCS",
        "us2015c": "2011-2015, ACS 5-year",
        "us2015d": "2011-2015, PRCS 5-year",
        "us2016a": "2016 ACS",
        "us2016b": "2016 PRCS",
        "us2016c": "2012-2016, ACS 5-year",
        "us2016d": "2012-2016, PRCS 5-year",
        "us2017a": "2017 ACS",
        "us2017b": "2017 PRCS",
        "us2017c": "2013-2017, ACS 5-year",
        "us2017d": "2013-2017, PRCS 5-year",
        "us2018a": "2018 ACS",
        "us2018b": "2018 PRCS",
        "us2018c": "2014-2018, ACS 5-year",
        "us2018d": "2014-2018, PRCS 5-year",
        "us2019a": "2019 ACS",
        "us2019b": "2019 PRCS",
        "us2019c": "2015-2019, ACS 5-year",
        "us2019d": "2015-2019, PRCS 5-year",
        "us2020a": "2020 ACS",
        "us2020c": "2016-2020, ACS 5-year",
        "us2020d": "2016-2020, PRCS 5-year",
        "us2021a": "2021 ACS",
        "us2021b": "2021 PRCS",
        "us2021c": "2017-2021, ACS 5-year",
        "us2021d": "2017-2021, PRCS 5-year",
        "us2022a": "2022 ACS",
        "us2022b": "2022 PRCS",
        "us2022c": "2018-2022, ACS 5-year",
        "us2022d": "2018-2022, PRCS 5-year",
    }


@pytest.mark.vcr
def test_get_pages(live_api_client: IpumsApiClient):
    """
    Test API pages generator.
    """
    page1 = next(live_api_client._get_pages(collection="usa", endpoint="extracts", page_size=5))
    assert len(page1["data"]) == 5
