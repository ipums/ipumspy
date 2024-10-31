"""
Classes for requesting IPUMS metadata via the IPUMS API
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class IpumsMetadata:
    """
    Basic object to request and store metadata for an IPUMS resource
    """

    _metadata_type = {}

    def __init_subclass__(cls, metadata_type: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.metadata_type = metadata_type
        IpumsMetadata._metadata_type[metadata_type] = cls


@dataclass
class DatasetMetadata(IpumsMetadata, metadata_type="dataset"):
    """
    Object to request and store metadata for an IPUMS dataset
    """

    collection: str
    """name of an IPUMS data collection"""
    name: str
    """IPUMS NHGIS dataset name"""
    description: Optional[str] = None
    """description of the dataset"""
    nhgis_id: Optional[str] = None
    """NHGIS ID used in NHGIS files to reference the dataset"""
    group: Optional[str] = None
    """group of datasets to which the dataset belongs"""
    sequence: Optional[str] = None
    """order in which the dataset will appear in the metadata API and extracts"""
    has_multiple_data_types: Optional[bool] = None
    """
    logical indicating whether multiple data types exist for the dataset 
        (for example, ACS datasets include both estimates and margins of error)
    """
    data_tables: Optional[List[Dict]] = None
    """
    dictionary containing names, codes, and descriptions for all data tables 
        available for the dataset
    """
    geog_levels: Optional[List[Dict]] = None
    """
    dictionary containing names, descriptions, and extent information for the geographic 
        levels available for the dataset
    """
    geographic_instances: Optional[List[Dict]] = None
    """
    dictionary containing names and descriptions for all valid geographic extents 
        for the dataset
    """
    breakdowns: Optional[List[Dict]] = None
    """
    dictionary containing names, types, descriptions, and breakdown values for all breakdowns 
        available for the dataset.
    """

    def __post_init__(self):
        self._path = f"metadata/datasets/{self.name}"


@dataclass
class TimeSeriesTableMetadata(IpumsMetadata, metadata_type="time_series_table"):
    """
    Object to request and store metadata for an IPUMS time series table
    """

    collection: str
    """name of an IPUMS data collection"""
    name: str
    """IPUMS NHGIS time series table name"""
    description: Optional[str] = None
    """description of the time series table"""
    geographic_integration: Optional[str] = None
    """
    The method by which the time series table aligns geographic units
        across time. Nominal integration indicates that geographic units 
        are aligned by name (disregarding changes in unit boundaries). 
        Standardized integration indicates that data from multiple time 
        points are standardized to the indicated year's census units
    """
    sequence: Optional[str] = None
    """order in which the time series table will appear in the metadata API and extracts"""
    time_series: Optional[List[Dict]] = None
    """dictionary containing names and descriptions for the individual time series available for the time series table"""
    years: Optional[List[Dict]] = None
    """dictionary containing information on the available data years for the time series table"""
    geog_levels: Optional[List[Dict]] = None
    """dictionary containing names and descriptions for the geographic levels available for the time series table"""

    def __post_init__(self):
        self._path = f"metadata/time_series_tables/{self.name}"


@dataclass
class DataTableMetadata(IpumsMetadata, metadata_type="data_table"):
    """
    Object to request and store metadata for an IPUMS data table
    """

    collection: str
    """name of an IPUMS data collection"""
    name: str
    """IPUMS data table name"""
    dataset_name: str
    """name of the dataset to which this data table belongs"""
    description: Optional[str] = None
    """description of the data table"""
    universe: Optional[str] = None
    """the statistical population measured by this data table"""
    nhgis_code: Optional[str] = None
    """
    the code identifying the data table in the extract. Variables in the extract 
        data will include column names prefixed with this code
    """
    sequence: Optional[str] = None
    """order in which the data table will appear in the metadata API and extracts"""
    variables: Optional[List[Dict]] = None
    """dictionary containing variable descriptions and codes for the variables included in the data table"""

    def __post_init__(self):
        self._path = f"metadata/datasets/{self.dataset_name}/data_tables/{self.name}"
