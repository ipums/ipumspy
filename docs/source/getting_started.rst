.. ipumspy introduction

.. currentmodule:: ipumspy

Getting Started
===============

Installation
------------

This package requires that you have at least Python 3.9 installed.

Install with ``pip``:

.. code:: bash

    pip install ipumspy

Install with ``conda``:

.. code:: bash
    
    conda install -c conda-forge ipumspy

.. _ipumspy readers:

Read an IPUMS extract
---------------------

For microdata collections, ipumspy provides methods to parse DDI xml codebooks and load data files into 
pandas ``DataFrame`` objects. Both fixed-width and csv files are supported.

For example:

.. code:: python

    from ipumspy import readers, ddi

    ddi_codebook = readers.read_ipums_ddi(ddi/xml/file path/)
    ipums_df = readers.read_microdata(ddi_codebook, data/file/path)


IPUMS API Wrappers for Python
-----------------------------

ipumspy provides an easy-to-use Python wrapper for IPUMS API endpoints.

.. _get an api key:

Get an API Key
**************

To interact with the IPUMS API, you'll need to register for access with the IPUMS project you'll be 
using. If you have not yet registered, you can find the link to register for each 
project at the top of its website, which can be accessed from the `IPUMS homepage <https://ipums.org>`__.

Once you're registered, you'll be able to create an `API key <https://account.ipums.org/api_keys>`__.

For security reasons, we recommend storing your key in an environment variable rather than including it in your code. 
The Conda documentation provides 
`instructions for saving environment variables <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#saving-environment-variables>`__ 
in conda environments for different operating systems. The example code on this page assumes that the 
API key is stored in an environment variable called ``IPUMS_API_KEY``.

A Simple Example
****************

To request IPUMS data via API, initialize an API client using your API key:

.. code:: python

    import os
    from pathlib import Path
    from ipumspy import IpumsApiClient, MicrodataExtract, readers, ddi

    IPUMS_API_KEY = os.environ.get("IPUMS_API_KEY")
    
    ipums = IpumsApiClient(IPUMS_API_KEY)

Next, create an extract definition that contains the specifications for the data you wish to request and download. 
For instance, we can request 2012 Puerto Rico Community Survey data for age and sex from 
`IPUMS USA <https://usa.ipums.org/usa/>`__ with the following:

.. code:: python
    
    # Create an extract definition
    extract = MicrodataExtract(
        collection="usa",
        description="Sample USA extract",
        samples=["us2012b"],
        variables=["AGE", "SEX"],
    )

.. seealso::
    The :doc:`IPUMS API client page<ipums_api/index>` contains more detailed information on
    supported data collections and available extract definition parameters.
        

Submit the extract to the IPUMS servers. After waiting for the extract to finish processing, you can download the data:

.. code:: python

    # Submit the extract request
    ipums.submit_extract(extract)
    print(f"Extract submitted with id {extract.extract_id}")
    #> Extract submitted with id 1

    # Wait for the extract to finish
    ipums.wait_for_extract(extract)

    # Download the extract
    DOWNLOAD_DIR = Path(<your_download_dir>)
    ipums.download_extract(extract, download_dir=DOWNLOAD_DIR)

For microdata collections, you can load your data using ipumspy readers described :ref:`above<ipumspy readers>`:

.. code:: python

    # Get the DDI
    ddi_file = list(DOWNLOAD_DIR.glob("*.xml"))[0]
    ddi = readers.read_ipums_ddi(ddi_file)

    # Get the data
    ipums_df = readers.read_microdata(ddi, DOWNLOAD_DIR / ddi.file_description.filename)

Aggregate data collection data can be loaded with other python libraries. See :ref:`reading-aggregate-data` for
examples.

For additional information about the IPUMS API as well as technical documentation, visit the 
`IPUMS developer portal <https://developer.ipums.org/>`__.