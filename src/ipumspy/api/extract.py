"""
Wrappers for payloads to ship to the IPUMS API
"""

from __future__ import annotations

import warnings
from typing import Any, Dict, List, Optional, Type, Union

import requests
import json
import inspect
from abc import ABC, abstractmethod

from ipumspy.ddi import Codebook

from dataclasses import dataclass, field
from .exceptions import IpumsExtractNotSubmitted


class ApiVersionWarning(Warning):
    pass


class ModifiedExtractWarning(Warning):
    pass


@dataclass
class IpumsObject(ABC):

    def update(self, attribute: str, value: Any):
        """
        Update Variable features

        Args:
            attribute: name of the object attribute to update
            value: values with which to update the `attribute`
        """
        if hasattr(self, attribute):
            setattr(self, attribute, value)
        else:
            raise KeyError(f"{type(self).__name__} has no attribute '{attribute}'.")

    @abstractmethod
    def build(self):
        pass


@dataclass
class Variable(IpumsObject):
    """
    IPUMS variable object to include in a ``MicrodataExtract`` object.

    Args:
        name: IPUMS variable name
        case_selections: Case selection specifications
        attached_characteristics: Attach characteristics specifications
        data_quality_flags: Flag to include the variable's associated data quality flags if they exist
    """

    name: str
    """IPUMS variable name"""
    preselected: Optional[bool] = False
    """Whether the variable is preselected. Defaults to False."""
    case_selections: Optional[Dict[str, List]] = field(default_factory=dict)
    """Case selection specifications"""
    attached_characteristics: Optional[List[str]] = field(default_factory=list)
    """Attach characteristics specifications"""
    data_quality_flags: Optional[bool] = False
    """Flag to include the variable's associated data quality flags if they exist"""

    def __post_init__(self):
        self.name = self.name.upper()

    def build(self):
        """Format Variable information for API Extract submission"""
        built_var = self.__dict__.copy()
        # don't repeat the variable name
        built_var.pop("name")
        # adhere to API schema camelCase convention
        built_var["caseSelections"] = built_var.pop("case_selections")
        built_var["attachedCharacteristics"] = built_var.pop("attached_characteristics")
        built_var["dataQualityFlags"] = built_var.pop("data_quality_flags")
        return built_var


@dataclass
class Sample(IpumsObject):
    """
    IPUMS sample object to include in a ``MicrodataExtract`` object.

    Args:
        id: IPUMS sample id
    """

    id: str
    """IPUMS sample id"""
    description: Optional[str] = ""
    """IPUMS sample description"""

    def __post_init__(self):
        self.id = self.id.lower()

    def build(self):
        """Format Sample information for API Extract submission"""
        raise NotImplementedError


@dataclass
class TimeUseVariable(IpumsObject):
    """
    IPUMS time use variable to include in a ``MicrodataExtract`` object.

    Args:
        name: IPUMS time use variable name
        owner: email address associated with your IPUMS account. Only required for user-defined time use variables.
    """

    name: str
    """IPUMS time use variable name"""
    owner: Optional[str] = ""
    """email address associated with your IPUMS account. Only required for user-defined Time Use Variables."""

    def __post_init__(self):
        self.name = self.name.lower()

    def build(self):
        """Format Time Use Variable information for API Extract submission"""
        built_tuv = self.__dict__.copy()
        # don't repeat the variable name
        built_tuv.pop("name")
        # only include the owner field if one is specified
        if self.owner != "":
            if "@" not in self.owner:
                raise ValueError(
                    "'owner' must be the email address associated with your IPUMS user account."
                )
            else:
                built_tuv["owner"] = built_tuv.pop("owner")
        else:
            built_tuv.pop("owner")
        return built_tuv


@dataclass
class Dataset(IpumsObject):
    """
    IPUMS dataset object to include in an ``AggregateDataExtract`` object.

    Args:
        name: IPUMS dataset name
        data_tables: IPUMS data tables to extract from this dataset
        geog_levels: Geographic level(s) at which to obtain data for this dataset
        years: Years for which to obtain data for this dataset (use ``['*']`` to select all years)
        breakdown_values: Breakdown values to apply to this dataset
    """

    name: str
    """IPUMS dataset name"""
    data_tables: List[str]
    """IPUMS data tables to extract from this dataset"""
    geog_levels: List[str]
    """Geographic level(s) at which to obtain data for this dataset"""
    years: Optional[List[str]] = field(default_factory=list)
    """Years for which to obtain data for this dataset (use ``['*']`` to select all years)"""
    breakdown_values: Optional[List[str]] = field(default_factory=list)
    """Breakdown values to apply to this dataset"""

    def __post_init__(self):
        self.years = [str(yr) for yr in self.years]

    def build(self):
        """Format dataset information for API Extract submission"""
        built_dataset = self.__dict__.copy()
        # don't repeat the dataset name
        built_dataset.pop("name")
        # adhere to API schema camelCase convention
        built_dataset["dataTables"] = built_dataset.pop("data_tables")
        built_dataset["geogLevels"] = built_dataset.pop("geog_levels")
        built_dataset["years"] = built_dataset.pop("years")
        built_dataset["breakdownValues"] = built_dataset.pop("breakdown_values")

        return built_dataset


@dataclass
class TimeSeriesTable(IpumsObject):
    """
    IPUMS time series table object to include in an ``AggregateDataExtract`` object.

    Args:
        name: IPUMS time series table name
        geog_levels: Geographic level(s) at which to obtain data for this time series table. Use ``["*"]`` to select all years
        years: Years for which to obtain data for this time series table
    """

    name: str
    """IPUMS time series table name"""
    geog_levels: List[str]  # required parameter
    """Geographic level(s) at which to obtain data for this time series table"""
    years: Optional[Union[List[str], List[int]]] = field(default_factory=list)
    """Years for which to obtain data for this time series table"""

    def __post_init__(self):
        self.name = self.name.upper()
        self.years = [str(yr) for yr in self.years]

    def build(self):
        """Format time series table information for API Extract submission"""
        built_tst = self.__dict__.copy()
        # don't repeat the time series table name
        built_tst.pop("name")
        # adhere to API schema camelCase convention
        built_tst["geogLevels"] = built_tst.pop("geog_levels")
        built_tst["years"] = built_tst.pop("years")

        return built_tst


@dataclass
class Shapefile(IpumsObject):
    """
    IPUMS shapefile object to include in an ``AggregateDataExtract`` object.

    Args:
        name: IPUMS shapefile name
    """

    name: str
    """IPUMS shapefile name"""

    def build(self):
        """Format shapefile information for API Extract submission"""
        raise NotImplementedError


def _unpack_samples_dict(dct: dict) -> List[Sample]:
    return [Sample(id=samp) for samp in dct.keys()]


def _unpack_variables_dict(dct: dict) -> List[Variable]:
    vars = []
    for var in dct.keys():
        var_obj = Variable(name=var)
        # this feels dumb, but the best way to avoid KeyErrors
        # that is coming to my brain at the moment
        if "preselected" in dct[var]:
            var_obj.update("preselected", dct[var]["preselected"])
        if "caseSelections" in dct[var]:
            var_obj.update("case_selections", dct[var]["caseSelections"])
        if "attachedCharacteristics" in dct[var]:
            var_obj.update(
                "attached_characteristics", dct[var]["attachedCharacteristics"]
            )
        if "dataQualityFlags" in dct[var]:
            var_obj.update("data_quality_flags", dct[var]["dataQualityFlags"])
        vars.append(var_obj)
    return vars


def _unpack_tuv_dict(dct: dict) -> List[TimeUseVariable]:
    tuvs = []
    for i in dct.keys():
        tuv_obj = TimeUseVariable(name=i)
        if "owner" in dct[i]:
            tuv_obj.update("owner", dct[i]["owner"])
        tuvs.append(tuv_obj)
    return tuvs


def _unpack_dataset_dict(dct: dict) -> List[Dataset]:
    datasets = []
    for dataset in dct.keys():
        dataset_obj = Dataset(
            name=dataset,
            data_tables=dct[dataset]["dataTables"],
            geog_levels=dct[dataset]["geogLevels"],
        )
        if "years" in dct[dataset]:
            dataset_obj.update("years", dct[dataset]["years"])
        if "breakdownValues" in dct[dataset]:
            dataset_obj.update("breakdown_values", dct[dataset]["breakdownValues"])
        datasets.append(dataset_obj)
    return datasets


def _unpack_tst_dict(dct: dict) -> List[TimeSeriesTable]:
    time_series_tables = []
    for time_series_table in dct.keys():
        time_series_table_obj = TimeSeriesTable(
            name=time_series_table, geog_levels=dct[time_series_table]["geogLevels"]
        )
        if "years" in dct[time_series_table]:
            time_series_table_obj.update("years", dct[time_series_table]["years"])
        time_series_tables.append(time_series_table_obj)

    return time_series_tables


def _unpack_shapefiles_dict(dct: dict) -> List[Shapefile]:
    return [Shapefile(name=shapefile) for shapefile in dct.keys()]


def _get_collection_type(collection: str) -> str:
    collection_types = {
        "usa": "microdata",
        "cps": "microdata",
        "ipumsi": "microdata",
        "atus": "microdata",
        "ahtus": "microdata",
        "mtus": "microdata",
        "nhis": "microdata",
        "meps:": "microdata",
        "nhgis": "aggregate_data",
    }

    return collection_types[collection]


def _camel_to_snake(key):
    # don't mess with case for boolean values
    if isinstance(key, bool):
        return key
    cap_idx = [0] + [
        key.index(l, i) for i, l in enumerate(key) if l.isupper() and i != 0
    ]
    parts_list = [key[i:j].lower() for i, j in zip(cap_idx, cap_idx[1:] + [None])]
    snake = "_".join(parts_list)
    return snake


class BaseExtract:
    _collection_type_to_extract: Dict[(str, str), Type[BaseExtract]] = {}

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

    def __init_subclass__(cls, collection_type: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.collection_type = collection_type
        BaseExtract._collection_type_to_extract[collection_type] = cls
        # cls.collection = collection
        # BaseExtract._collection_to_extract[collection] = cls

    def _kwarg_warning(self, kwargs_dict: Dict[str, Any]):
        # raise kwarg warnings if they exist
        if "warnings" in kwargs_dict.keys():
            newline = "\n"
            warnings.warn(
                f"This extract object has been modified from its original form in the following ways: "
                f"{newline.join(kwargs_dict['warnings'])}",
                ModifiedExtractWarning,
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
        str: The extract id associated with this extract, assigned by the ``IpumsApiClient``

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

    def _snake_to_camel(self, kwarg_dict):
        for key in list(kwarg_dict.keys()):
            # if the value of the kwarg is also a dict
            if isinstance(kwarg_dict[key], dict):
                self._snake_to_camel(kwarg_dict[key])

            # create camelCase equivalent
            key_list = key.split("_")
            # join capitalized versions of all parts except the first
            camelized = "".join([k.capitalize() for k in key_list[1:]])
            # prepend the first part
            camel_key = f"{key_list[0]}{camelized}"
            # add the camelCase key
            kwarg_dict[camel_key] = kwarg_dict[key]
            # pop the snake_case key
            kwarg_dict.pop(key)
        return kwarg_dict

    def _validate_list_args(self, list_arg, arg_obj):
        # this bit feels extra sketch, but it seems like a better solution
        # than just having the BaseExtract(**kwargs) method of instantiating
        # an extract object quietly leave out variable-level extract features

        # before diving into any duplicate validation, make sure the list argument the user provided
        # is only strings or only IPUMS objects. Raise a useful error and ask the user to fix themselves
        if not all(isinstance(i, str) for i in list_arg) and not all(
            isinstance(i, IpumsObject) for i in list_arg
        ):
            raise TypeError(
                f"The items in {list_arg} must all be string type or {arg_obj} type."
            )
        if isinstance(list_arg, dict) and arg_obj is Variable:
            args = _unpack_variables_dict(list_arg)
            return args
        elif isinstance(list_arg, dict) and arg_obj is Sample:
            args = _unpack_samples_dict(list_arg)
            return args
        elif isinstance(list_arg, dict) and arg_obj is TimeUseVariable:
            args = _unpack_tuv_dict(list_arg)
            return args
        elif isinstance(list_arg, dict) and arg_obj is Dataset:
            args = _unpack_dataset_dict(list_arg)
            return args
        elif isinstance(list_arg, dict) and arg_obj is TimeSeriesTable:
            args = _unpack_tst_dict(list_arg)
            return args
        elif isinstance(list_arg, dict) and arg_obj is Shapefile:
            args = _unpack_shapefiles_dict(list_arg)
            return args

        # Make sure extracts don't get built with duplicate variables or samples
        # if the argument is a list of objects, make sure there are not objects with duplicate names
        elif all(isinstance(i, arg_obj) for i in list_arg):
            try:
                if len(set([i.name for i in list_arg])) < len(list_arg):
                    # Because Variable objects can have the same name but differet feature specifications
                    # force the user to fix this themselves
                    raise ValueError(
                        f"Duplicate Variable objects are not allowed in IPUMS Extract definitions."
                    )
                else:
                    # return the list of objects
                    return list_arg
            except AttributeError:
                if len(set([i.id for i in list_arg])) < len(list_arg):
                    # Because Sample objects can have the same id but differet feature specifications
                    # force the user to fix this themselves
                    raise ValueError(
                        f"Duplicate Sample objects are not allowed in IPUMS Extract definitions."
                    )
                else:
                    # return the list of objects
                    return list_arg
        elif all(isinstance(i, str) for i in list_arg):
            # if duplicate string names are specified, just drop the duplicates
            # and return a list of the relevant objects
            unique_list = list(dict.fromkeys(list_arg))
            return [arg_obj(i) for i in unique_list]

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


class MicrodataExtract(BaseExtract, collection_type="microdata"):
    def __init__(
        self,
        collection: str,
        samples: Union[List[str], List[Sample]],
        variables: Union[List[str], List[Variable]],
        description: str = "",
        data_format: str = "fixed_width",
        data_structure: Dict = {"rectangular": {"on": "P"}},
        time_use_variables: Union[List[str], List[TimeUseVariable]] = None,
        **kwargs,
    ):
        """
        Class for defining an extract for an IPUMS microdata collection.

        Args:
            collection: name of an IPUMS data collection
            samples: list of sample IDs from an IPUMS microdata collection
            variables: list of variable names from an IPUMS microdata collection
            description: short description of your extract
            data_format: fixed_width and csv supported
            data_structure: nested dict with "rectangular", "hierarchical", or "household-only" as first-level key.
                            "rectangular" extracts require further specification of "on" : <record type>.
                            Default {"rectangular": "on": "P"} requests an extract rectangularized on the "P" record.
            time_use_variables: a list of IPUMS Time Use Variable names or Objects. This argument is only valid for IPUMS ATUS,
                                MTUS, and AHTUS data collections. If the list contains user-created Time Use Variables, these
                                must be passed as a list of TimeUseVariable objects with the 'owner' field specified.

        Keyword Args:
            data_quality_flags: a boolean value which, if True, adds the data quality flags for each variable included in the `variables` list
                                if a data quality flag exists for that variable.
            sample_members: a dictionary of non-default sample members to include for Time Use collections where keys are strings
                            indicating sample member type and values are boolean. This argument is only valid for IPUMS ATUS,
                            MTUS, and AHTUS data collections. Valid keys include 'include_non_respondents' and 'include_household_members'.
            case_select_who: indicates how to interpret any case selections included for variables in the extract. ``"individuals"``
                            includes records for all individuals who match the specified case selections, while ``"households"``
                            includes records for all members of each household that contains an individual who matches the specified case selections.
        """

        super().__init__()
        self.collection_type = self.collection_type
        """IPUMS collection type"""
        self.collection = collection
        self.samples = self._validate_list_args(samples, Sample)
        self.variables = self._validate_list_args(variables, Variable)
        if description == "":
            self.description = f"My IPUMS {collection.upper()} extract"
        else:
            self.description = description
        self.data_format = data_format
        self.data_structure = data_structure
        self.api_version = (
            self.extract_api_version(kwargs)
            if len(kwargs.keys()) > 0
            else self.api_version
        )
        """IPUMS API version number"""
        # check kwargs for conflicts with defaults
        self._kwarg_warning(kwargs)
        # make the kwargs camelCase
        self.kwargs = self._snake_to_camel(kwargs)

        # I don't love this, but it also seems overkill to make a seperate extract class
        # just for these features
        self.time_use_variables = time_use_variables
        if self.time_use_variables is not None:
            # XXX remove when the server-side error messaging is improved
            if self.collection in ["atus", "mtus", "ahtus"]:
                self.time_use_variables = self._validate_list_args(
                    self.time_use_variables, TimeUseVariable
                )
            else:
                raise ValueError(
                    f"Time use variables are unavailable for the IPUMS {self.collection.upper()} data collection"
                )

    def build(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary to be passed to the IPUMS API
        as a JSON string
        """
        built = {
            "description": self.description,
            "dataFormat": self.data_format,
            "dataStructure": self.data_structure,
            "samples": {sample.id: {} for sample in self.samples},
            "variables": {
                variable.name.upper(): variable.build() for variable in self.variables
            },
            "collection": self.collection,
            "version": self.api_version,
            **self.kwargs,
        }

        if self.time_use_variables is not None:
            built["timeUseVariables"] = {
                tuv.name.upper(): tuv.build() for tuv in self.time_use_variables
            }

        # XXX shoehorn fix until server-side bug is fixed
        if self.collection == "meps":
            for variable in built["variables"].keys():
                built["variables"][variable].pop("attachedCharacteristics")

        return built

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
        """
        self._update_variable_feature(variable, "attached_characteristics", of)

    def add_data_quality_flags(
        self, variable: Union[Variable, str, List[Variable], List[str]]
    ):
        """
        A method to update existing IPUMS Extract Variable objects to include that
        variable's data quality flag in the extract if it exists.

        Args:
            variable: a Variable object or a string variable name

        """
        if isinstance(variable, list):
            for v in variable:
                self._update_variable_feature(v, "data_quality_flags", True)
        else:
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


class AggregateDataExtract(BaseExtract, collection_type="aggregate_data"):
    def __init__(
        self,
        collection: str,
        datasets: Optional[List[Dataset]] = [],
        time_series_tables: Optional[List[TimeSeriesTable]] = [],
        shapefiles: Optional[Union[List[str], List[Shapefile]]] = [],
        description: str = "",
        data_format: str = "csv_no_header",
        geographic_extents: Optional[List[str]] = None,
        tst_layout: str = "time_by_column_layout",
        breakdown_and_data_type_layout: str = "single_file",
        **kwargs,
    ):
        """
        Class for defining an extract request for an IPUMS aggregate data collection.

        Args:
            datasets: list of ``Dataset`` objects
            time_series_tables: list of ``TimeSeriesTable`` objects
            shapefiles: list of shapefile names
            description: short description of your extract
            data_format: desired format of the extract data file. One of ``"csv_no_header"``, ``"csv_header"``, or ``"fixed_width"``.
            geographic_extents: Geographic extents to use for all ``datasets`` and ``time_series_tables`` in the extract definition (for instance, to
                                to obtain data within a particular state).
            tst_layout: desired data layout for all  ``time_series_tables`` in the extract definition.
                        One of ``"time_by_column_layout"`` (default), ``"time_by_row_layout"``, or ``"time_by_file_layout"``.
            breakdown_and_data_type_layout: desired layout of any ``datasets`` that have multiple data types or breakdown values. Either
                                            ``"single_file"`` (default) or ``"separate files"``
        """

        super().__init__()

        self.collection = collection
        self.collection_type = self.collection_type
        """IPUMS collection type"""

        self.datasets = self._validate_list_args(datasets, Dataset)
        self.time_series_tables = self._validate_list_args(
            time_series_tables, TimeSeriesTable
        )
        self.shapefiles = self._validate_list_args(shapefiles, Shapefile)

        if (
            len(self.datasets) == 0
            and len(self.time_series_tables) == 0
            and len(self.shapefiles) == 0
        ):
            raise ValueError(
                "At least one dataset, time series table, or shapefile must be specified."
            )

        self.description = description
        self.data_format = data_format
        self.geographic_extents = geographic_extents
        self.breakdown_and_data_type_layout = breakdown_and_data_type_layout
        self.tst_layout = tst_layout

        self.api_version = (
            self.extract_api_version(kwargs)
            if len(kwargs.keys()) > 0
            else self.api_version
        )
        """IPUMS API version number"""

        # check kwargs for conflicts with defaults
        self._kwarg_warning(kwargs)
        # make the kwargs camelCase
        self.kwargs = self._snake_to_camel(kwargs)

    def build(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary to be passed to the IPUMS API
        as a JSON string
        """

        built = {
            "description": self.description,
            "dataFormat": self.data_format,
            "collection": self.collection,
            "version": self.api_version,
            **self.kwargs,
        }

        if self.datasets is not None:
            built["datasets"] = {
                dataset.name: dataset.build() for dataset in self.datasets
            }
            built["breakdownAndDataTypeLayout"] = self.breakdown_and_data_type_layout

            if self.geographic_extents is not None:
                built["geographicExtents"] = self.geographic_extents

        if self.time_series_tables is not None:
            built["timeSeriesTables"] = {
                tst.name.upper(): tst.build() for tst in self.time_series_tables
            }
            built["timeSeriesTableLayout"] = self.tst_layout

        if self.shapefiles is not None:
            built["shapefiles"] = [shapefile.name for shapefile in self.shapefiles]

        return built


def extract_from_dict(dct: Dict[str, Any]) -> Union[BaseExtract, List[BaseExtract]]:
    """
    Convert an extract that is currently specified as a dictionary (usually from a file)
    into a ``BaseExtract`` object. If multiple extracts are specified, return a
    ``List[BaseExtract]``.

    Args:
        dct: The dictionary specifying the extract(s)

    Returns:
        The extract(s) specified by ``dct``
    """
    if "extracts" in dct:
        # We are returning several extracts
        return [extract_from_dict(extract) for extract in dct["extracts"]]

    def _make_snake_ext(ext_dict):
        obj_keys = [
            "variables",
            "samples",
            "timeUseVariables",
            "datasets",
            "timeSeriesTables",
        ]

        for key in ext_dict.keys():
            if isinstance(ext_dict[key], dict):
                if key not in obj_keys:
                    ext_dict[key] = _make_snake_ext(ext_dict[key])
        return {_camel_to_snake(k): v for k, v in ext_dict.items()}

    ext_dct = _make_snake_ext(dct)
    collection_type = _get_collection_type(dct["collection"])

    extract_class = BaseExtract._collection_type_to_extract[collection_type]
    extract = extract_class(**ext_dct)

    return extract


def extract_to_dict(extract: Union[BaseExtract, List[BaseExtract]]) -> Dict[str, Any]:
    """
    Convert an extract object to a dictionary (usually to write to a file).
    If multiple extracts are specified, return a ``dict`` object.

    Args:
        extract: A submitted IPUMS extract object or list of submitted IPUMS extract objects

    Returns:
        The extract(s) specified as a dictionary
    """
    dct = {}
    if isinstance(extract, list):
        dct["extracts"] = [extract_to_dict(ext) for ext in extract]
        return dct
    try:
        ext = extract.extract_info
        # just retain the definition part
        return ext["extractDefinition"]

    except ValueError:
        raise IpumsExtractNotSubmitted(
            "Extract has not been submitted and so has no json response"
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
