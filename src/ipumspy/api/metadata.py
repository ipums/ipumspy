"""
Classes for requesting IPUMS metadata via the IPUMS API
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from abc import ABC


@dataclass(init=False)
class IpumsMetadata(ABC):
    """
    Basic class to request and store metadata for an arbitrary IPUMS resource
    """

    _metadata_classes = {}

    def __init__(self, **kwargs):
        pass

    def __init_subclass__(cls, metadata_type: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.metadata_type = metadata_type
        IpumsMetadata._metadata_classes[metadata_type] = cls


@dataclass(init=False)
class DatasetMetadata(IpumsMetadata, metadata_type="dataset"):
    """
    Class to request and store metadata for an IPUMS dataset

    Args:
        collection: name of an IPUMS data collection
        name: Name of an IPUMS dataset associated with the indicated collection
    """

    collection: str
    """name of an IPUMS data collection"""
    name: str
    """IPUMS NHGIS dataset name"""
    nhgis_id: Optional[str] = field(default=None, init=False)
    """NHGIS ID used in NHGIS files to reference the dataset"""
    group: Optional[str] = field(default=None, init=False)
    """group of datasets to which the dataset belongs"""
    sequence: Optional[str] = field(default=None, init=False)
    """order in which the dataset will appear in the metadata API and extracts"""
    has_multiple_data_types: Optional[bool] = field(default=None, init=False)
    """
    logical indicating whether multiple data types exist for the dataset 
        (for example, ACS datasets include both estimates and margins of error)
    """
    data_tables: Optional[List[Dict]] = field(default=None, init=False)
    """
    dictionary containing names, codes, and descriptions for all data tables 
        available for the dataset
    """
    geog_levels: Optional[List[Dict]] = field(default=None, init=False)
    """
    dictionary containing names, descriptions, and extent information for the geographic 
        levels available for the dataset
    """
    geographic_instances: Optional[List[Dict]] = field(default=None, init=False)
    """
    dictionary containing names and descriptions for all valid geographic extents 
        for the dataset
    """
    breakdowns: Optional[List[Dict]] = field(default=None, init=False)
    """
    dictionary containing names, types, descriptions, and breakdown values for all breakdowns 
        available for the dataset.
    """

    def __init__(self, collection, name, **kwargs):
        self.collection = collection
        self.name = name
        self._path = f"metadata/datasets/{self.name}"

        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass(init=False)
class TimeSeriesTableMetadata(IpumsMetadata, metadata_type="time_series_table"):
    """
    Class to request and store metadata for an IPUMS time series table

    Args:
        collection: IPUMS collection associated with this time series table
        name: Name of the time series table for which to retrieve metadata
    """

    collection: str
    """name of an IPUMS data collection"""
    name: str
    """IPUMS NHGIS time series table name"""
    description: Optional[str] = field(default=None, init=False)
    """description of the time series table"""
    geographic_integration: Optional[str] = field(default=None, init=False)
    """
    The method by which the time series table aligns geographic units
        across time. Nominal integration indicates that geographic units 
        are aligned by name (disregarding changes in unit boundaries). 
        Standardized integration indicates that data from multiple time 
        points are standardized to the indicated year's census units
    """
    sequence: Optional[str] = field(default=None, init=False)
    """order in which the time series table will appear in the metadata API and extracts"""
    time_series: Optional[List[Dict]] = field(default=None, init=False)
    """dictionary containing names and descriptions for the individual time series available for the time series table"""
    years: Optional[List[Dict]] = field(default=None, init=False)
    """dictionary containing information on the available data years for the time series table"""
    geog_levels: Optional[List[Dict]] = field(default=None, init=False)
    """dictionary containing names and descriptions for the geographic levels available for the time series table"""

    def __init__(self, collection, name, **kwargs):
        self.collection = collection
        self.name = name
        self._path = f"metadata/time_series_tables/{self.name}"

        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass(init=False)
class DataTableMetadata(IpumsMetadata, metadata_type="data_table"):
    """
    Class to request and store metadata for an IPUMS data table

    Args:
        collection: IPUMS collection associated with this data table
        name: Name of the data table for which to retrieve metadata
        dataset_name: Name of the dataset containing this data table
    """

    collection: str
    """name of an IPUMS data collection"""
    name: str
    """IPUMS data table name"""
    dataset_name: str
    """name of the dataset to which this data table belongs"""
    description: Optional[str] = field(default=None, init=False)
    """description of the data table"""
    universe: Optional[str] = field(default=None, init=False)
    """the statistical population measured by this data table"""
    nhgis_code: Optional[str] = field(default=None, init=False)
    """
    the code identifying the data table in the extract. Variables in the extract 
        data will include column names prefixed with this code
    """
    sequence: Optional[str] = field(default=None, init=False)
    """order in which the data table will appear in the metadata API and extracts"""
    variables: Optional[List[Dict]] = field(default=None, init=False)
    """dictionary containing variable descriptions and codes for the variables included in the data table"""

    def __init__(self, collection, name, dataset_name, **kwargs):
        self.collection = collection
        self.name = name
        self.dataset_name = dataset_name
        self._path = f"metadata/datasets/{self.dataset_name}/data_tables/{self.name}"

        for key, value in kwargs.items():
            setattr(self, key, value)
