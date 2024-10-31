.. ipumspy documentation for reading microdata files

.. currentmodule:: ipumspy

Reading IPUMS Data
==================

Reading IPUMS Microdata Extracts
--------------------------------

Reading IPUMS data into a pandas data frame using ipumspy requires a fixed-width or csv IPUMS extract data file and an IPUMS xml DDI file.

To read a fixed-width rectangular IPUMS extract:

.. code:: python

    # Get the DDI
    ddi = readers.read_ipums_ddi(path/to/ddi_file.xml)
    # Get the data
    ipums_df = readers.read_microdata(ddi, path/to/data_file.dat.gz)

As these files are often large, users may wish to filter or read in chunks. The :meth:`readers.read_microdata_chunked()` method can help. For example, the following reads only rows from Minnesota:

.. code:: python

    iter_microdata = read_microdata_chunked(ddi, chunksize=1000)
    df = pd.concat([df[df["STATEFIP"] == 27] for df in iter_microdata])

The :meth:`readers.read_hierarchical_microdata()` method is for reading hierarchical extracts. By default, this method returns a dictionary with a data frame for each record type. Record types are keys, data frames are values.

.. code:: python

    extract_dict = readers.read_hierarchical_microdata(ddi, 
                                                       path/to/hierarhcical_file.dat.gz)

To get a single data frame for a hierarchical extract, set the ``as_dict`` flag in :meth:`readers.read_hierarchical_microdata()` to ``False``.

IPUMS Variable Metadata
***********************

Microdata extracts include a DDI codebook (XML) file which contains metadata about the contents of an
extract, including variables. 

Variable Descriptions
~~~~~~~~~~~~~~~~~~~~~

The :class:`VariableDescription<ipumspy.ddi.VariableDescription>` objects built from the DDI codebook 
provide easy access to variable metadata. These can be returned using the :meth:`.get_variable_info()` method.

Assuming that our data file contains the SEX variable, we could use the following:

.. code:: python

    from ipumspy import readers
    import pandas as pd

    # read ddi and data
    ddi_codebook = readers.read_ipums_ddi(path/to/ddi/xml/file)
    ipums_df = readers.read_microdata(ddi_codebook, path/to/data/file)

    # get VariableDescription for SEX
    sex_info = ddi_codebook.get_variable_info("SEX")

    # see codes and labels for SEX
    print(sex_info.codes)
    #> {'Male': 1, 'Female': 2}

    # see variable description for SEX
    print(sex_info.description)
    #> SEX reports whether the person was male or female.

You can use variable metadata to interpret the contents of your extract and make data processing
and analysis decision accordingly.

More on Value Labels
~~~~~~~~~~~~~~~~~~~~

For categorical variables, you can filter your data using value labels instead of
numeric values. For example, the following code retains only the female respondents 
in the ``ipums_df`` data frame from above, using the ``"Female"`` label:

.. code:: python

    # retrieve the VaribleDescription for the variable SEX
    sex_info = ddi_codebook.get_variable_info("SEX")

    # Filter to records where SEX is Female
    women = ipums_df[ipums_df["SEX"] == sex_info.codes["Female"]]

It is possible to filter both using labels as well as numeric values.
The following retains only women over the age of 16 in ``ipums_df``:

.. code:: python

    adult_women = ipums_df[(ipums_df["SEX"] == sex_info.codes["Female"]) &
                           (ipums_df["AGE"] > 16)]

.. _reading-aggregate-data:

Reading IPUMS Aggregate Data Extracts
-------------------------------------

By default, extracts for aggregate data projects are provided in csv format, 
and therefore don't include DDI metadata files found in microdata extracts. While aggregate data
collections do provide codebook metadata files, they are in text format and are designed to be 
human-readable rather used to parse the fixed-width files common for microdata projects.

.. attention::
    Aggregate data codebook files contain the citation information for these collections; if you 
    use IPUMS data in a publication or report, please cite appropriately.

When downloaded, IPUMS aggregate data extract files are compressed, and may include multiple files
in the provided zip archive. The easiest way to load  data from these files is to use Python's 
``zipfile`` module.

For instance, to list the names of the files contained in an extract:

.. code:: python

    from zipfile import ZipFile
    import pandas as pd

    fname = "<path/to/zip/file>"

    # a list of individual file names from inside the .zip file
    names = ZipFile(fname).namelist()
    #> ['nhgis0025_csv/nhgis0025_ds120_1990_county_codebook.txt', 'nhgis0025_csv/nhgis0025_ds120_1990_county.csv']

You can use the names of the containing files to identify the files you wish to load. Here, we use
pandas to load the compressed csv file:

.. code:: python

    # Read first data file in the extract
    with ZipFile(fname) as z:
        with z.open(names[1]) as f:
            data = pd.read_csv(f)

.. note::
    IPUMS NHGIS does allow you to request an extract in fixed-width format, but ipumspy does not
    provide methods to parse these files as it does for Microdata because IPUMS NHGIS does not provide
    the necessary DDI codebook.

Shapefile data is delivered in a nested zipfile that can also be unpacked using the ``ZipFile`` module and read using third party libraries such as geopandas.

Reading Non-Extractable IPUMS Collections
-----------------------------------------

The `IPUMS YRBSS <https://www.ipums.org/projects/ipums-yrbss>`__ and `IPUMS NYTS <https://www.ipums.org/projects/ipums-nyts>`__ data 
collections are not accessed through the IPUMS extract system, but are available for download in their entirety. ipumspy has 
functionality to download these datasets (:py:meth:`~noextract.download_noextract_data()`) and parse the YAML format codebooks 
that come packaged with the ipumspy library (:py:meth:`~noextract.read_noextract_codebook()`). This codebook object can 
then be used to read the downloaded dataset into a pandas data frame using :py:meth:`~readers.read_microdata()` as with other 
IPUMS microdata extracts retrieved via the IPUMS extract system.