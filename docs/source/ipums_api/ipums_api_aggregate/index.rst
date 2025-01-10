.. ipumspy documentation for aggregate data

.. currentmodule:: ipumspy

Aggregate Data Extracts
=======================

IPUMS aggregate data collections distribute aggregated statistics for a set of geographic units.

Currently, `IPUMS NHGIS <https://www.nhgis.org/>`__ is the only aggregate data collection
supported by the IPUMS API.

Extract Objects
---------------

Construct an extract for an IPUMS aggregate data collection using the 
:class:`AggregateDataExtract<ipumspy.api.extract.AggregateDataExtract>` class.
An ``AggregateDataExtract`` must contain an IPUMS collection ID 
and at least one data source. IPUMS NHGIS provides 3 different types of data sources:

- Datasets/data tables
- Time series tables
- Shapefiles

We also recommend providing an extract description to make it easier to identify and 
retrieve your extract in the future.

For example:

.. code:: python

   from ipumspy import AggregateDataExtract, Dataset

   extract = AggregateDataExtract(
      collection="nhgis",
      description="An NHGIS extract example",
      datasets=[
         Dataset(name="1990_STF1", data_tables=["NP1", "NP2"], geog_levels=["county"])
      ]
   )

This instantiates an ``AggregateDataExtract`` object for the IPUMS NHGIS data collection
that includes a request for county-level data from tables NP1 (total population) and NP2 (total families) of 
the 1990 STF 1 decennial census file.

After instantiation, an ``AggregateDataExtract`` object can be
:ref:`submitted to the API <submit-extract>` for processing.

.. note::
   The IPUMS API provides a set of metadata endpoints for aggregate data collections that allow you
   to browse available data sources and identify their associated API codes.

   You can also browse metadata interactively through the `NHGIS Data Finder <https://data2.nhgis.org/main>`_.

Datasets + Data Tables
----------------------

An IPUMS **dataset** contains a collection of **data tables** that each correspond to a particular tabulated summary statistic. 
A dataset is distinguished by the years, geographic levels, and topics that it covers. For instance, 2021 1-year data from the 
American Community Survey (ACS) is encapsulated in a single dataset. In other cases, a single census product will be split into 
multiple datasets, typically based on the lowest-level geography for which a set of tables is available. See the 
`NHGIS documentation <https://www.nhgis.org/overview-nhgis-datasets>`_ for more details.

To request data contained in an IPUMS dataset, you need to specify the name of the dataset, name of the data table(s) to request
from that dataset, and the geographic level at which those tables should be aggregated.

Use the :class:`Dataset <ipumspy.api.extract.Dataset>` class to specify these parameters.

.. code:: python

   extract = AggregateDataExtract(
      collection="nhgis",
      description="An NHGIS example extract",
      datasets=[
         Dataset(name="2000_SF1a", data_tables=["NP001A", "NP031A"], geog_levels=["state"])
      ],
   )

Some datasets span multiple years and require a selection of ``years``:

.. code:: python

   extract = AggregateDataExtract(
      collection="nhgis",
      description="An NHGIS example extract",
      datasets=[
         Dataset(
            name="1988_1997_CBPa",
            data_tables=["NT004"],
            geog_levels=["county"],
            years=[1988, 1989, 1990],
        )
      ],
   )

.. tip::
   To select all years in a dataset, use ``years=["*"]``.

You can also optionally request specific `breakdown values <https://www.nhgis.org/frequently-asked-questions-faq#breakdowns>`__
for a dataset with the ``breakdown_values`` keyword argument:

.. code:: python

   extract = AggregateDataExtract(
      collection="nhgis",
      description="An NHGIS example extract",
      datasets=[
         Dataset(
               name="2000_SF1a",
               data_tables=["NP001A", "NP031A"],
               geog_levels=["state"],
               breakdown_values=["bs21.ge01", "bs21.ge43"],  # Urban + Rural breakdowns
         )
      ],
   )

By default, the first available breakdown (typically, the total count) will be selected. When retrieving a
previously submitted extract from the IPUMS API, you may notice a breakdown value code present in the extract
definition despite not explicitly requesting one when submitting the extract.

For datasets with multiple breakdowns or data types (e.g., the American Community Survey contains both estimates
and margins of error), you can request that the data for each be provided in separate files or together in a
single file using the ``breakdown_and_data_type_layout`` argument.

Dataset + Data Table Metadata
+++++++++++++++++++++++++++++

Use the :class:`DatasetMetadata <ipumspy.api.metadata.DatasetMetadata>` data class to browse the available
specification options for a particular dataset and identify the codes to use when
requesting data from the API:

.. code:: python

   from ipumspy import IpumsApiClient, DatasetMetadata

   ipums = IpumsApiClient(os.environ.get("IPUMS_API_KEY"))

   ds = ipums.get_metadata(DatasetMetadata("nhgis", "2000_SF1a"))

The returned object will contain the metadata for the requested dataset. For example:

.. code:: python

   # Description of the dataset
   ds.description

   # Dictionary of data table codes for this dataset
   ds.data_tables

   # etc...

You can also request metadata for individual data tables using the same workflow with the :class:`DataTableMetadata <ipumspy.api.metadata.DataTableMetadata>` data class.

Geographic Extent Selection
+++++++++++++++++++++++++++

When working with small geographies it can be computationally intensive to work with
nationwide data. To avoid this problem, you can request data from a specific geographic area 
using the ``geographic_extents`` argument.

The following extract requests ACS 5-year sex-by-age counts at the census block group level, but
only includes block groups that fall within Alabama and Arkansas (identified by their FIPS codes with
a trailing 0):

.. code:: python

   extract = AggregateDataExtract(
      collection="nhgis",
      description="Extent selection example",
      datasets=[
         Dataset(name="2018_2022_ACS5a", data_tables=["B01001"], geog_levels=["blck_grp"]),
         Dataset(name="2017_2021_ACS5a", data_tables=["B01001"], geog_levels=["blck_grp"])
      ],
      geographic_extents=["010", "050"]
   )

.. tip::
   You can see available extent selection API codes, if any, in the ``geographic_instances`` attribute of
   a submitted :class:`DatasetMetadata <ipumspy.api.metadata.DatasetMetadata>` object.

Note that extent selection is *not* a dataset-specific parameter. That is, the selected extents
are applied to all datasets in the extract. It is not possible to request different extents for different
datasets in a single extract.

Time Series Tables
------------------

IPUMS NHGIS also provides `time series tables <https://www.nhgis.org/time-series-tables>`_—longitudinal data sources that link comparable statistics from multiple
U.S. censuses in a single package. A table is comprised of one or more related time series, each 
of which describes a single summary statistic measured at multiple times for a given geographic level.

Use the :class:`TimeSeriesTable<ipumspy.api.extract.TimeSeriesTable>` class to add time series tables
to your extract request.

Time series tables are already associated with a specific summary statistic, so they don't require an additional
selection of data tables as is required for NHGIS datasets. However, you will need to specify the geographic
level for the data:

.. code:: python

   from ipumspy import AggregateDataExtract, TimeSeriesTable

   extract = AggregateDataExtract(
      collection="nhgis",
      description="An NHGIS example extract: time series tables",
      time_series_tables=[TimeSeriesTable("CW3", geog_levels=["county", "state"])],
   )

By default, a time series table request will provide data for all years available for that time series table.
You can select a subset of available years with the ``years`` argument:

.. code:: python
   
   extract = AggregateDataExtract(
      collection="nhgis",
      description="An NHGIS example extract: time series tables",
      time_series_tables=[
         TimeSeriesTable("CW3", geog_levels=["county", "state"], years=[1990, 2000])
      ],
   )

For extract requests that contain time series tables, you can indicate the desired layout of the time
series data with the ``tst_layout`` argument. Timepoints can either be arranged in columns, rows, or split
into separate files (by default, time is arranged across columns).

.. code:: python
   
   extract = AggregateDataExtract(
      collection="nhgis",
      description="An NHGIS example extract: time series tables",
      time_series_tables=[
         TimeSeriesTable("CW3", geog_levels=["county", "state"], years=[1990, 2000])
      ],
      tst_layout="time_by_row_layout",
   )

As with datasets and data tables, you can request metadata about the available specification options
for a specific time series table using the :class:`TimeSeriesTableMetadata <ipumspy.api.metadata.TimeSeriesTableMetadata>` class.

Shapefiles
----------

IPUMS **shapefiles** contain geographic data for a given geographic level and year. 
Typically, these files are composed of polygon geometries containing the boundaries of census reporting areas.

Because there are no additional selection parameters for shapefiles, you can include them in your request
simply by specifying their names:

.. code:: python

   AggregateDataExtract(
      collection="nhgis",
      shapefiles=["us_county_2021_tl2021", "us_county_2020_tl2020"]
   )

Multiple Data Sources
---------------------

You can request any combination of datasets, time series tables, and shapefiles in a single extract.
For instance, to request spatial boundary data to go along with the tabular data requested in a set of
datasets:

.. code:: python

   # Total state-level population from 2000 and 2010 decennial census
   extract = AggregateDataExtract(
      collection="nhgis",
      description="An NHGIS example extract",
      datasets=[
         Dataset(name="2000_SF1a", data_tables=["NP001A"], geog_levels=["state"]),
         Dataset(name="2010_SF1a", data_tables=["P1"], geog_levels=["state"])
      ],
      shapefiles=["us_state_2000_tl2010", "us_state_2010_tl2010"]
   )

In some cases, data table codes are consistent across datasets. This is often the case for the American Community Survey
(ACS) datasets. This makes it easy to build an extract request for a specific data table for
several ACS years at once using list comprehensions. For instance:

.. code:: python

   acs1_names = ["2017_ACS1", "2018_ACS1", "2019_ACS1"]
   acs1_specs = [
      Dataset(name, data_tables=["B01001"], geog_levels=["state"]) for name in acs1_names
   ]

   # Total state-level population from 2017-2019 ACS 1-year estimates
   extract = AggregateDataExtract(
      collection="nhgis",
      description="An NHGIS example extract",
      datasets=acs1_specs,
   )

Data Format
-----------

By default, NHGIS extracts are provided in CSV format with only a single header row.
If you like, you can request that your CSV data include a second header row containing
a description of each column's contents by setting ``data_format="csv_header"``.

You can also request your data in
fixed-width format if so desired. Note that unlike for microdata projects, NHGIS does
not provide DDI codebook files (in XML format), which allow ipumspy to parse
microdata fixed-width files. Thus, loading an NHGIS fixed width file will require
manual work to parse the file correctly.

Supplemental Data
-----------------

IPUMS NHGIS also provides some data products via direct download, without the need to create
an extract request. These sources are available via the IPUMS API. However, since you access
these files directly, you must know a file's URL before you can download it.

Many NHGIS supplemental data files can be found under the "Supplemental Data" heading on the left side of the
`NHGIS homepage <https://www.nhgis.org/>`_.  See the IPUMS 
`developer documentation page <https://developer.ipums.org/docs/v2/apiprogram/apis/nhgis/#ipums-nhgis-supplemental-data>`_ 
for all supported supplemental data endpoints and advice on how to convert file URLs found on the website into
acceptable API request URLs.

Once you've identified a file's location, you can use the``ipumspy`` :py:meth:`.get` method to download it. For
instance, to download a state-level NHGIS crosswalk file, we could use the following:

.. code:: python

   ipums = IpumsApiClient(os.environ.get("IPUMS_API_KEY"))

   file_name = "nhgis_blk2010_blk2020_10.zip"
   url = f"{ipums.base_url}/supplemental-data/nhgis/crosswalks/nhgis_blk2010_blk2020_state/{file_name}"

   download_path = "<your-download-path-here>"

   with ipums.get(url, stream=True) as response:
      with open(download_path, "wb") as outfile:
         for chunk in response.iter_content(chunk_size=8192):
               outfile.write(chunk)

