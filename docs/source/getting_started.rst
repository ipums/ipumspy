.. ipumspy introduction

.. currentmodule:: ipumspy

Getting Started
===============

Installation
------------

This package requires that you have at least Python 3.6 installed.

Install with `pip`:

.. code:: bash

    pip install ipumspy

Or conda:

.. code:: bash

    conda install -c conda-forge ipumspy

Read an IPUMS extract
---------------------

The following code parses an IPUMS extract DDI xml codebook and data file and returns a pandas data frame.
Both fixed-width and csv files are supported.

.. code:: python

    from ipumspy import readers, ddi

    ddi_codebook = readers.read_ipums_ddi([ddi xml file path])
    ipums_df = readers.read_microdata(ddi_codebook, [data file path])


IPUMS API Wrappers for Python
-----------------------------

``ipumspy`` provides an easy-to-use Python wrapper for IPUMS API endpoints.

Quick Start
***********

Once you have created a user account for your data collection of interest (currently only IPUMS USA is available via API) and generated an API key...

.. code:: python

    import itertools as its
    import time
    from pathlib import Path

    from ipumspy import IpumsApiClient, UsaExtract

    IPUMS_API_KEY = your_api_key
    DOWNLOAD_DIR = Path(your_download_dir)

    ipums = IpumsApiClient(IPUMS_API_KEY)

To submit an IPUMS USA extract, a list of sample IDs and a list of IPUMS USA variable names.

IPUMS USA sample IDs can be found `here <https://usa.ipums.org/usa-action/samples/sample_ids>`_.

IPUMS USA variables can be browsed `here <https://usa.ipums.org/usa-action/variables/group>`_.

.. code:: python

    # Submit an API extract request
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
    )
    ipums.submit_extract(extract)
    print(f"Extract submitted with id {extract.extract_id}")

    # wait for the extract to finish
    ipums.wait_for_extract(extract)

    # Download the extract
    ipums.download_extract(extract, download_dir=DOWNLOAD_DIR)

    # Get the DDI
    ddi_file = list(DOWLOAD_DIR.glob("*.xml"))[0]
    ddi = ipumspy.read_ipums_ddi(ddi_file)

    # Get the data
    ipums_df = ipumspy.read_microdata(ddi, DOWNLOAD_DIR / ddi.file_description.filename)
