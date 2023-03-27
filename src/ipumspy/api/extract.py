"""
Wrappers for payloads to ship to the IPUMS API
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, Union

import requests
import json

from ipumspy.ddi import Codebook
from ipumspy.utilities import CollectionInformation

from .exceptions import IpumsExtractNotSubmitted


class DefaultCollectionWarning(Warning):
    pass


class ApiVersionWarning(Warning):
    pass


@dataclass
class Variable:
    name: str
    preselected: Optional[bool] = False
    case_selections: Optional[Dict[str, List]] = field(default_factory=dict)
    attached_characteristics: Optional[List[str]] = field(default_factory=list)
    data_quality_flags: Optional[bool] = False

    def __post_init__(self):
        self.name = self.name.upper()

    def update(self, attribute: str, value: Any):
        if hasattr(self, attribute):
            setattr(self, attribute, value)
        else:
            raise KeyError(f"Variable has no attribute '{attribute}'.")

    def build(self):
        built_var = self.__dict__.copy()
        # don't repeat the variable name
        built_var.pop("name")
        # adhere to API schema camelCase convention
        built_var["caseSelections"] = built_var.pop("case_selections")
        built_var["attachedCharacteristics"] = built_var.pop("attached_characteristics")
        built_var["dataQualityFlags"] = built_var.pop("data_quality_flags")
        return built_var


@dataclass
class Sample:
    id: str

    def __post_init__(self):
        self.id = self.id.lower()

    def update(self, attribute: str, value: Any):
        if hasattr(self, attribute):
            setattr(self, attribute, value)
        else:
            raise KeyError(f"Sample has no attribute '{attribute}'.")


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

    def extract_api_version(self, kwargs_dict: Dict[str, Any]) -> str:
        # check to see if version is specified in kwargs_dict
        if "version" in kwargs_dict.keys() or "api_version" in kwargs_dict.keys():
            try:
                if kwargs_dict["version"] == self.api_version:
                    # collectin kwarg is the same as default, nothing to do
                    return self.api_version
                # this will only get hit if the extract object has already been submitted
                # or if an api_version other than None was explicitly passed to BaseExtract
                elif (
                    kwargs_dict["version"] != self.api_version
                    and self.api_version is not None
                ):
                    warnings.warn(
                        f"The IPUMS API version specified in the extract definition is not the most recent. "
                        f"Extract definition IPUMS API version: {kwargs_dict['version']}; most recent IPUMS API version: {self.api_version}",
                        ApiVersionWarning,
                    )
                    # update extract object api version to reflect
                    return kwargs_dict["version"]
                # In all other instances, return the version from the kwargs dict
                # If this version is illegal, it will raise an IpumsAPIAuthenticationError upon submission
                else:
                    return kwargs_dict["version"]
            except KeyError:
                # no longer supporting beta extract schema
                raise NotImplementedError(
                    f"The IPUMS API version specified in the extract definition is not supported by this version of ipumspy."
                )
        # if no api_version is specified, use default IpumsApiClient version
        else:
            return self.api_version

    def _update_variable_feature(self, variable, feature, specification):
        if isinstance(variable, Variable):
            variable.update(feature, specification)
        elif isinstance(variable, str):
            for var in self.variables:
                if var.name == variable:
                    var.update(feature, specification)
                    break
            else:
                raise ValueError(f"{variable} is not part of this extract.")
        else:
            raise TypeError(
                f"Expected a string or Variable object; {type(variable)} received."
            )

    def attach_characteristics(self, variable: Union[Variable, str], of: List[str]):
        """
        A method to update existing IPUMS Extract Variable objects
        with the IPUMS attach characteristics feature.

        Args:
            variable: a Variable object or a string variable name
            of: a list of records for which to create a variable on the individual record.
                Allowable values include "mother", "father", "spouse", "head". For IPUMS
                collection that identify same sex couples can also accept "mother2" and "father2"
                values in this list. If either "<parent>" or "<parent>2" values are included,
                their same sex counterpart will automatically be included in the extract.

        Returns: A Variable object with the `attached_characteristics` attribute with the
                 value of the `of` argument
        """
        self._update_variable_feature(variable, "attached_characteristics", of)

    def add_data_quality_flags(self, variable: Union[Variable, str]):
        """
        A method to update existing IPUMS Extract Variable objects to include that
        variable's data quality flag in the extract if it exists.

        Args:
            variable: a Variable object or a string variable name

        Returns: A Variable object with the `data_quality_fags` attribute set to True
        """
        self._update_variable_feature(variable, "data_quality_flags", True)

    def select_cases(
        self,
        variable: Union[Variable, str],
        values: List[Union[int, str]],
        general: bool = True,
    ):
        """
        A method to update existing IPUMS Extract Variable objects to select cases
        with the specified values of that IPUMS variable.

        Args:
            variable: a Variable object or a string variable name
            values: a list of values for which to select records
            general: set to False to select cases on detailed codes. Defaults to True.

        Returns: A Variable object with the `select_cases` attribute with general or detailed codes specified for selection.
        """
        # stringify values
        values = [str(v) for v in values]
        if general:
            self._update_variable_feature(
                variable, "case_selections", {"general": values}
            )
        else:
            self._update_variable_feature(
                variable, "case_selections", {"detailed": values}
            )


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
        samples: Union[List[str], List[Sample]],
        variables: Union[List[str], List[Variable]],
        description: str = "My IPUMS USA extract",
        data_format: str = "fixed_width",
        data_structure: Dict = {"rectangular": {"on": "P"}},
        **kwargs,
    ):
        """
        Defining an IPUMS USA extract.

        Args:
            samples: list of IPUMS USA sample IDs
            variables: list of IPUMS USA variable names
            description: short description of your extract
            data_format: fixed_width and csv supported
            data_structure: nested dict with "rectangular" or "hierarchical" as first-level key.
                            "rectangular" extracts require further specification of "on" : <record type>.
                            Default {"rectangular": "on": "P"} requests an extract rectangularized on the "P" record.
        """

        super().__init__()
        if all(isinstance(sample, str) for sample in samples):
            self.samples = [Sample(sample) for sample in samples]
        else:
            self.samples = samples
        if all(isinstance(variable, str) for variable in variables):
            self.variables = [Variable(variable) for variable in variables]
        else:
            self.variables = variables
        self.description = description
        self.data_format = data_format
        self.data_structure = data_structure
        self.collection = self.collection
        """Name of an IPUMS data collection"""
        self.api_version = (
            self.extract_api_version(kwargs)
            if len(kwargs.keys()) > 0
            else self.api_version
        )
        """IPUMS API version number"""
        # check kwargs for conflicts with defaults
        self._kwarg_warning(kwargs)

    @classmethod
    def from_api_response(cls, api_response: Dict[str, Any]) -> UsaExtract:
        return cls(
            samples=list(api_response["extractDefinition"]["samples"]),
            variables=list(api_response["extractDefinition"]["variables"]),
            data_format=api_response["extractDefinition"]["dataFormat"],
            data_structure=api_response["extractDefinition"]["dataStructure"],
            description=api_response["extractDefinition"]["description"],
            api_version=api_response["extractDefinition"]["version"],
            collection=api_response["extractDefinition"]["collection"],
        )

    def build(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary to be passed to the IPUMS API
        as a JSON string
        """
        return {
            "description": self.description,
            "dataFormat": self.data_format,
            "dataStructure": self.data_structure,
            "samples": {sample.id: {} for sample in self.samples},
            "variables": {
                variable.name.upper(): variable.build() for variable in self.variables
            },
            "collection": self.collection,
            "version": self.api_version,
        }


class CpsExtract(BaseExtract, collection="cps"):
    def __init__(
        self,
        samples: Union[List[str], List[Sample]],
        variables: Union[List[str], List[Variable]],
        description: str = "My IPUMS CPS extract",
        data_format: str = "fixed_width",
        data_structure: Dict = {"rectangular": {"on": "P"}},
        **kwargs,
    ):
        """
        Defining an IPUMS CPS extract.

        Args:
            samples: list of IPUMS CPS sample IDs
            variables: list of IPUMS CPS variable names
            description: short description of your extract
            data_format: fixed_width and csv supported
            data_structure: nested dict with "rectangular" or "hierarchical" as first-level key.
                            "rectangular" extracts require further specification of "on" : <record type>.
                            Default {"rectangular": "on": "P"} requests an extract rectangularized on the "P" record.
        """

        super().__init__()
        if all(isinstance(sample, str) for sample in samples):
            self.samples = [Sample(sample) for sample in samples]
        else:
            self.samples = samples
        if all(isinstance(variable, str) for variable in variables):
            self.variables = [Variable(variable) for variable in variables]
        else:
            self.variables = variables
        self.description = description
        self.data_format = data_format
        self.data_structure = data_structure
        self.collection = self.collection
        """Name of an IPUMS data collection"""
        self.api_version = (
            self.extract_api_version(kwargs)
            if len(kwargs.keys()) > 0
            else self.api_version
        )
        """IPUMS API version number"""

        # check kwargs for conflicts with defaults
        self._kwarg_warning(kwargs)

    @classmethod
    def from_api_response(cls, api_response: Dict[str, Any]) -> CpsExtract:
        return cls(
            samples=list(api_response["extractDefinition"]["samples"]),
            variables=list(api_response["extractDefinition"]["variables"]),
            data_format=api_response["extractDefinition"]["dataFormat"],
            data_structure=api_response["extractDefinition"]["dataStructure"],
            description=api_response["extractDefinition"]["description"],
            api_version=api_response["extractDefinition"]["version"],
            collection=api_response["extractDefinition"]["collection"],
        )

    def build(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary to be passed to the IPUMS API
        as a JSON string
        """
        return {
            "description": self.description,
            "dataFormat": self.data_format,
            "dataStructure": self.data_structure,
            "samples": {sample.id: {} for sample in self.samples},
            "variables": {
                variable.name.upper(): variable.build() for variable in self.variables
            },
            "collection": self.collection,
            "version": self.api_version,
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
        # pop keys created after submission
        [ext.pop(key) for key in ["downloadLinks", "number", "status"]]
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
    extract_info["dataStructure"] = ddi_codebook.file_description.structure
    # DDI does not reflect when extract is requested in CSV or other format
    # so this method will default to specifying fixed_width (.dat)
    extract_info["dataFormat"] = "fixed_width"

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
