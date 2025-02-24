"""
Classes for requesting IPUMS metadata via the IPUMS API
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


@dataclass
class IpumsMetadata(ABC):
    """
    Class to request and store metadata for an arbitrary IPUMS resource. Use a subclass to request
    metadata for a particular type of resource.
    """

    def populate(self, metadata_response_dict: dict):
        """
        Update IpumsMetadata objects with attributes from API response.

        Args:
            metadata_response_dict: JSON response from IPUMS metadata API
        """
        for attribute in metadata_response_dict.keys():
            if hasattr(self, attribute):
                setattr(self, attribute, metadata_response_dict[attribute])
            else:
                raise KeyError(f"{type(self).__name__} has no attribute '{attribute}'.")

    @property
    @abstractmethod
    def supported_collections(self):
        """
        Collections that support this metadata class
        """
        pass

    def _validate_collection(self):
        if self.collection not in self.supported_collections:
            raise ValueError(
                f"{type(self).__name__} is not a valid metadata type for the {self.collection} collection."
            )


@dataclass
class DatasetMetadata(IpumsMetadata):
    """
    Class to request and store metadata for an IPUMS dataset

    Args:
        collection: name of an IPUMS data collection
        name: Name of an IPUMS dataset included in the collection
    """

    collection: str
    """Name of an IPUMS data collection"""
    name: str
    """IPUMS dataset name"""
    nhgis_id: Optional[str] = field(default=None, init=False)
    """ID used in IPUMS files to reference the dataset"""
    group: Optional[str] = field(default=None, init=False)
    """Group of datasets to which the dataset belongs"""
    description: Optional[str] = field(default=None, init=False)
    """Description of the dataset from IPUMS"""
    sequence: Optional[str] = field(default=None, init=False)
    """Order in which the dataset will appear in the metadata API and extracts"""
    has_multiple_data_types: Optional[bool] = field(default=None, init=False)
    """
    Logical indicating whether multiple data types exist for the dataset 
        (e.g., estimates and margins of error)
    """
    data_tables: Optional[List[Dict]] = field(default=None, init=False)
    """
    Dictionary containing names, codes, and descriptions for all data tables 
        available for the dataset
    """
    geog_levels: Optional[List[Dict]] = field(default=None, init=False)
    """
    Dictionary containing names, descriptions, and extent information for the geographic 
        levels available for the dataset
    """
    geographic_instances: Optional[List[Dict]] = field(default=None, init=False)
    """
    Dictionary containing names and descriptions for the geographic extents available for the
        dataset, if any
    """
    breakdowns: Optional[List[Dict]] = field(default=None, init=False)
    """
    Dictionary containing names, types, descriptions, and breakdown values for all breakdowns 
        available for the dataset
    """

    def __post_init__(self):
        self._path = f"metadata/datasets/{self.name}"
        self._validate_collection()

    @property
    def supported_collections(self):
        return ["nhgis"]


@dataclass
class TimeSeriesTableMetadata(IpumsMetadata):
    """
    Class to request and store metadata for an IPUMS time series table.

    Args:
        collection: IPUMS collection that contains time series tables
        name: Name of the time series table for which to retrieve metadata
    """

    collection: str
    """Name of an IPUMS data collection"""
    name: str
    """IPUMS time series table name"""
    description: Optional[str] = field(default=None, init=False)
    """Description of the time series table"""
    geographic_integration: Optional[str] = field(default=None, init=False)
    """The method by which the time series table aligns geographic units across time 
        ("nominal" integration aligns units by name, disregarding changes 
        in unit boundaries; "standardized" integration provides data from multiple 
        times for a single census's geographic units)
    """
    sequence: Optional[str] = field(default=None, init=False)
    """Order in which the time series table will appear in the metadata API and extracts"""
    time_series: Optional[List[Dict]] = field(default=None, init=False)
    """Dictionary containing names and descriptions for the individual time series available for the time series table"""
    years: Optional[List[Dict]] = field(default=None, init=False)
    """Dictionary containing information on the available data years for the time series table"""
    geog_levels: Optional[List[Dict]] = field(default=None, init=False)
    """Dictionary containing names and descriptions for the geographic levels available for the time series table"""
    geographic_instances: Optional[List[Dict]] = field(default=None, init=False)
    """Dictionary containing names and descriptions for all valid geographic extents available for any year in the time series table"""

    def __post_init__(self):
        self._path = f"metadata/time_series_tables/{self.name}"
        self._validate_collection()

    @property
    def supported_collections(self):
        return ["nhgis"]


@dataclass
class DataTableMetadata(IpumsMetadata):
    """
    Class to request and store metadata for an IPUMS data table

    Args:
        collection: IPUMS collection associated with this data table
        name: Name of the data table for which to retrieve metadata
        dataset_name: Name of the dataset containing this data table
    """

    collection: str
    """Name of an IPUMS data collection"""
    name: str
    """IPUMS data table name"""
    dataset_name: str
    """Name of the dataset to which this data table belongs"""
    description: Optional[str] = field(default=None, init=False)
    """Description of the data table"""
    universe: Optional[str] = field(default=None, init=False)
    """The statistical population measured by this data table"""
    nhgis_code: Optional[str] = field(default=None, init=False)
    """
    The code identifying the data table in the extract (variables in the 
        extract data will include column names prefixed with this code)
    """
    sequence: Optional[str] = field(default=None, init=False)
    """Order in which the data table will appear in the metadata API and extracts"""
    variables: Optional[List[Dict]] = field(default=None, init=False)
    """Dictionary containing variable descriptions and codes for the variables included in the data table"""

    def __post_init__(self):
        self._path = self._path = (
            f"metadata/datasets/{self.dataset_name}/data_tables/{self.name}"
        )
        self._validate_collection()

    @property
    def supported_collections(self):
        return ["nhgis"]
