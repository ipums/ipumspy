.. reading_data

.. currentmodule:: ipumspy

Reading IPUMS Data
==================

Reading IPUMS Extracts
----------------------

Reading IPUMS data into a Pandas data frame using ``ipumspy`` requires a fixed-width or csv IPUMS extract data file and an IPUMS xml DDI file.

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

Reading Non-Extractable IPUMS Collections
-----------------------------------------

The `IPUMS YRBSS <https://www.ipums.org/projects/ipums-yrbss>`__ and `IPUMS NYTS <https://www.ipums.org/projects/ipums-nyts>`__ data collections are not accessed through the IPUMS extract system, but are available for download in their entirety. ``ipumspy`` has functionality to download these datasets (:py:meth:`~noextract.download_noextract_data()`) and parse the yml format codebooks that come packaged with the ``ipumspy`` library (:py:meth:`~noextract.read_noextract_codebook()`). This codebook object can then be used to read the downloaded dataset into a Pandas data frame using :py:meth:`~readers.read_microdata()` as with other IPUMS datasets retrieved via the IPUMS extract system.