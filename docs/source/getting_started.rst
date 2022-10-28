.. ipumspy introduction

.. currentmodule:: ipumspy

Getting Started
===============

Installation
------------

This package requires that you have at least Python 3.7 installed.

Install with ``pip``:

.. code:: bash

    pip install ipumspy

Install with ``conda``:

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

``ipumspy`` provides an easy-to-use Python wrapper for IPUMS Microdata Extract API endpoints. Note that the IPUMS Microdata Extract API is still in beta!

Quick Start
***********

Once you have created a user account for your data collection of interest (currently only `IPUMS USA <https://uma.pop.umn.edu/usa/user/new?return_url=https%3A%2F%2Fusa.ipums.org%2Fusa-action%2Fmenu>`__ and `IPUMS CPS <https://uma.pop.umn.edu/cps/user/new?return_url=https%3A%2F%2Fcps.ipums.org%2Fusa-action%2Fmenu>`__ are available via API) and generated an API key:

.. code:: python

    from pathlib import Path

    from ipumspy import IpumsApiClient, UsaExtract, readers, ddi

    IPUMS_API_KEY = your_api_key
    DOWNLOAD_DIR = Path(your_download_dir)

    ipums = IpumsApiClient(IPUMS_API_KEY)

Note that for security reasons it is recommended that you store your IPUMS API key in an environment variable rather than including it in your code.

To define an IPUMS USA extract, you need to pass a list of sample IDs and a list of IPUMS USA variable names.

IPUMS USA sample IDs can be found on the `IPUMS USA website <https://usa.ipums.org/usa-action/samples/sample_ids>`__.

IPUMS USA variables can be browsed via the `IPUMS USA extract web UI <https://usa.ipums.org/usa-action/variables/group>`__.

Source variables can be requested using their short or long form variable names. Short form source variable names can be viewed by clicking `Display Options` on the `Select Data` page and selecting the `short` option under `Source variable names`.

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
    ddi_file = list(DOWNLOAD_DIR.glob("*.xml"))[0]
    ddi = readers.read_ipums_ddi(ddi_file)

    # Get the data
    ipums_df = readers.read_microdata(ddi, DOWNLOAD_DIR / ddi.file_description.filename)

If you lose track of the ``extract`` object for any reason, you may check the status
and download the extract using only the name of the ``collection`` and the ``extract_id``.

.. code:: python

    # check the extract status
    extract_status = ipums.extract_status(extract=[extract_id], collection=[collection_name])
    print(f"extract {extract_id} is {extract_status}")

    # when the extract status is "completed", then download
    ipums.download_extract(extract=[extract_id], collection=[collection_name])

Specifying an Extract as a File
*******************************

A goal of IPUMS-py is to make it easier to share IPUMS extracts with other researchers.
For instance, we envision being able to include an ``ipums.yml`` file to your analysis
code which would allow other researchers to download *exactly* the extract that you
utilize in your own analysis.

To pull the extract we specified made above, create a file called ``ipums.yml`` that
contains the following:

.. code:: yaml

    description: Simple IPUMS extract
    collection: usa
    api_version: beta
    samples:
      - us2012b
    variables:
      - AGE
      - SEX

Then you can run the following code:

.. code:: python

    import yaml
    from ipumspy import extract_from_dict

    with open("ipums.yml") as infile:
        extract = extract_from_dict(yaml.safe_load(infile))

Alternatively, you can utilize the :doc:`CLI <cli>`.

For more information on the IPUMS Microdata Extract API, visit the `IPUMS developer portal <https://beta.developer.ipums.org/>`__.