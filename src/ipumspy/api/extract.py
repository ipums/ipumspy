"""
Wrappers for payloads to ship to the IPUMS API
"""
from __future__ import annotations

import warnings
from typing import Any, Dict, List, Optional, Type, Union

import requests
import json

from ipumspy.ddi import Codebook
from ipumspy.utilities import CollectionInformation

from .exceptions import IpumsExtractNotSubmitted


class DefaultCollectionWarning(Warning):
    pass


class BaseExtract:
    _collection_to_extract: Dict[(str, str), Type[BaseExtract]] = {}

    def __init__(self):
        """
        A wrapper around an IPUMS extract. In most cases, you
        probably want to use a subclass, but if a particular collection
        does not have an ``Extract`` currently built, you can use
        this wrapper directly.
        """

        self._id: Optional[int] = None
        self._info: Optional[Dict[str, Any]] = None
        self.api_version: Optional[str] = None

    def __init_subclass__(cls, collection: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.collection = collection
        BaseExtract._collection_to_extract[collection] = cls

    def _kwarg_warning(self, kwargs_dict: Dict[str, Any]):
        if not kwargs_dict:
            # no kwargs specified, nothing to do
            pass
        elif kwargs_dict["collection"] == self.collection:
            # collection kwarg is same as default, nothing to do
            pass
        elif kwargs_dict["collection"] != self.collection:
            warnings.warn(
                f"This extract object already has a default collection "
                f"{self.collection}. Collection Key Word Arguments "
                f"are ignored.",
                DefaultCollectionWarning,
            )

    def build(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary to be passed to the IPUMS API
        as a JSON string
        """
        raise NotImplementedError()

    @property
    def extract_id(self) -> int:
        """
        str:The extract id associated with this extract, assigned by the ``IpumsApiClient``

        Raises ``ValueError`` if the extract has no id number (probably because it has
        not be submitted to IPUMS)
        """
        if not self._id:
            raise ValueError("Extract has not been submitted so has no id number")
        return self._id

    @property
    def extract_info(self) -> Dict[str, Any]:
        """
        str: The API response recieved by the ``IpumsApiClient``

        Raises ``ValueError`` if the extract has no json response (probably because it
        has not bee submitted to IPUMS)
        """
        if not self._info:
            raise IpumsExtractNotSubmitted(
                "Extract has not been submitted and so has no json response"
            )
        else:
            return self._info


class OtherExtract(BaseExtract, collection="other"):
    def __init__(self, collection: str, details: Optional[Dict[str, Any]]):
        """
        A generic extract object for working with collections that are not
        yet officially supported by this API library
        """

        super().__init__()
        self.collection = collection
        """Name of an IPUMS data collection"""
        self.details = details
        """dictionary containing variable names and sample IDs"""

    def build(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary to be passed to the IPUMS API
        as a JSON string
        """
        return self.details


class UsaExtract(BaseExtract, collection="usa"):
    def __init__(
        self,
        samples: List[str],
        variables: List[str],
        description: str = "My IPUMS USA extract",
        data_format: str = "fixed_width",
        **kwargs,
    ):
        """
        Defining an IPUMS USA extract.

        Args:
            samples: list of IPUMS USA sample IDs
            variables: list of IPUMS USA variable names
            description: short description of your extract
            data_format: fixed_width and csv supported
        """

        super().__init__()
        self.samples = samples
        self.variables = variables
        self.description = description
        self.data_format = data_format
        self.collection = self.collection
        """Name of an IPUMS data collection"""

        # check kwargs for conflicts with defaults
        self._kwarg_warning(kwargs)

    @classmethod
    def from_api_response(cls, api_response: Dict[str, Any]) -> UsaExtract:
        return cls(
            samples=list(api_response["samples"]),
            variables=list(api_response["variables"]),
            data_format=api_response["data_format"],
            description=api_response["description"],
        )

    def build(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary to be passed to the IPUMS API
        as a JSON string
        """
        return {
            "description": self.description,
            "data_format": self.data_format,
            "data_structure": {"rectangular": {"on": "P"}},
            "samples": {sample: {} for sample in self.samples},
            "variables": {variable.upper(): {} for variable in self.variables},
            "collection": self.collection,
        }


class CpsExtract(BaseExtract, collection="cps"):
    def __init__(
        self,
        samples: List[str],
        variables: List[str],
        description: str = "My IPUMS CPS extract",
        data_format: str = "fixed_width",
        **kwargs,
    ):
        """
        Defining an IPUMS CPS extract.

        Args:
            samples: list of IPUMS CPS sample IDs
            variables: list of IPUMS CPS variable names
            description: short description of your extract
            data_format: fixed_width and csv supported
        """

        super().__init__()
        self.samples = samples
        self.variables = variables
        self.description = description
        self.data_format = data_format
        self.collection = self.collection
        """Name of an IPUMS data collection"""

        # check kwargs for conflicts with defaults
        self._kwarg_warning(kwargs)

    @classmethod
    def from_api_response(cls, api_response: Dict[str, Any]) -> CpsExtract:
        return cls(
            samples=list(api_response["samples"]),
            variables=list(api_response["variables"]),
            data_format=api_response["data_format"],
            description=api_response["description"],
        )

    def build(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary to be passed to the IPUMS API
        as a JSON string
        """
        return {
            "description": self.description,
            "data_format": self.data_format,
            "data_structure": {"rectangular": {"on": "P"}},
            "samples": {sample: {} for sample in self.samples},
            "variables": {variable.upper(): {} for variable in self.variables},
            "collection": self.collection,
        }


def extract_from_dict(dct: Dict[str, Any]) -> Union[BaseExtract, List[BaseExtract]]:
    """
    Convert an extract that is currently specified as a dictionary (usually from a file)
    into a BaseExtract object. If multiple extracts are specified, return a
    List[BaseExtract] objects.

    Args:
        dct: The dictionary specifying the extract(s)

    Returns:
        The extract(s) specified by dct
    """
    if "extracts" in dct:
        # We are returning several extracts
        return [extract_from_dict(extract) for extract in dct["extracts"]]

    if dct["collection"] in BaseExtract._collection_to_extract:
        # cosmetic procedure for when dct comes from json file
        for key in ["samples", "variables"]:
            if isinstance(dct[key], dict):
                dct[key] = list(dct[key].keys())

        return BaseExtract._collection_to_extract[dct["collection"]](**dct)

    return OtherExtract(dct["collection"], dct)


def extract_to_dict(extract: Union[BaseExtract, List[BaseExtract]]) -> Dict[str, Any]:
    """
    Convert an extract object to a dictionary (usually to write to a file).
    If multiple extracts are specified, return a dict object.

    Args:
        extract: IPUMS extract object or list of IPUMS extract objects

    Returns:
        The extract(s) specified as a dictionary
    """
    dct = {}
    if isinstance(extract, list):
        dct["extracts"] = [extract_to_dict(ext) for ext in extract]
        return dct
    try:
        ext = extract.extract_info
        ext["collection"] = extract.collection
        ext["api_version"] = extract.api_version
        # pop keys created after submission
        [ext.pop(key) for key in ["download_links", "number", "status"]]
        return ext

    except ValueError:
        raise IpumsExtractNotSubmitted(
            "Extract has not been submitted and so has no json response"
        )


def define_extract_from_ddi(
    ddi_codebook: Union[Codebook, List[Codebook]]
) -> Union[BaseExtract, List[BaseExtract]]:
    """
    Create a BaseExtract object from a parsed DDI codebook.

    Args:
        ddi_codebook: A parsed IPUMS DDI Codebook object or list of such objects

    Returns:
        A BaseExtract object with the data collection, samples, variables,
        and data structure specified by the DDI Codebook. Data format defaults
        to fixed-width.
    """
    if isinstance(ddi_codebook, list):
        return [define_extract_from_ddi(ddi) for ddi in ddi_codebook]
    collection = ddi_codebook.ipums_collection
    sample_ids_dict = CollectionInformation(collection).sample_ids

    # put extract info in a dict
    extract_info = {}
    extract_info["collection"] = collection
    extract_descs = ddi_codebook.samples_description
    extract_info["samples"] = [sample_ids_dict[desc] for desc in extract_descs]
    extract_info["variables"] = [vd.name for vd in ddi_codebook.data_description]
    extract_info["data_structure"] = ddi_codebook.file_description.structure
    # DDI does not reflect when extract is requested in CSV or other format
    # so this method will default to specifying fixed_width (.dat)
    extract_info["data_format"] = "fixed_width"

    # because the DDI doesn't have API version info, the extract will be submitted
    # with the default version of the API or one that the user specifies when
    # instantiating IpumsAPIClient
    return BaseExtract._collection_to_extract[extract_info["collection"]](
        **extract_info
    )


def save_extract_as_json(extract: Union[BaseExtract, List[BaseExtract]], filename: str):
    """
    Convenience method to save an IPUMS extract definition to a json file.

    Args:
        extract: IPUMS extract object or list of IPUMS extract objects
        filename: Path to json file to which to save the IPUMS extract object(s)
    """
    with open(filename, "w") as fileh:
        json.dump(extract_to_dict(extract), fileh, indent=4)


def define_extract_from_json(filename: str) -> Union[BaseExtract, List[BaseExtract]]:
    """
    Convenience method to convert an IPUMS extract definition or definitions stored
    in a json file into a BaseExtract object. If multiple extracts are specified,
    return a List[BaseExtract] objects.

    Args:
        filename: Json file containing IPUMS extract definitions

    Returns:
        The extract(s) specified in the json file
    """
    with open(filename, "r") as fileh:
        extract = extract_from_dict(json.load(fileh))

    return extract
