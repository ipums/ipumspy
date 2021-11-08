.. extracts

.. currentmodule:: ipumspy

IPUMS Extracts
==============

Extract Definition
------------------

An extract is defined by:

1. A data collection name
2. A list of IPUMS sample IDs from that collection
3. A list of IPUMS variable names from that collection

IPUMS metadata is not currently available via API. 
Sample IDs and IPUMS variable names can be browsed via the data collection's website. 
See the table below for data collection abreviations and links to sample IDs and variable browsing.
Note that not all IPUMS data collections are currently available via API. The table below will be
filled in as new IPUMS data collections become accessible via API.

.. list-table:: IPUMS data collections metadata
    :widths: 25 25 25 25
    :header-rows: 1
    :align: center

    * - IPUMS data collection
      - collection IDs
      - sample IDs
      - variable names
    * - IPUMS USA
      - usa
      - `here <https://usa.ipums.org/usa-action/samples/sample_ids>`__
      - `here <https://usa.ipums.org/usa-action/variables/group>`__

Extract Objects
---------------

Each IPUMS data collection that is accessible via API (currently just IPUMs USA) has its own extract class(?).
Using this class to create your extract object obviates the need to specify a data collection.

For example:

.. code:: python

    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
    )

creates an IPUMS USA extract object for the IPUMS USA data collection that includes the us2012b (2012 PRCS) sample, and the variables AGE and SEX.

Once an extract oject has been created, the extract object must be submitted to the API.

.. code:: python

    from ipumspy import IpumsApiClient, UsaExtract

    IPUMS_API_KEY = your_api_key
    DOWNLOAD_DIR = Path(your_download_dir)

    ipums = IpumsApiClient(IPUMS_API_KEY)

    # define your extract
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
    )

    # submit your extract
    ipums.submit_extract(extract)

Once an extract has been submitted, an extract ID number will be assigned to your extract.
You can use this extract ID number along with the data collection name to check on or download 
your extract later if you lose track of the original extract object.

Extract status
--------------

After your extract has been submitted, you can check it's status using 

.. code:: python

    ipums.extract_status(extract)

returns:

.. code:: python

    'started'

While IPUMS retains all of a user's extract definitions, after a certain period, 
the extract data and syntax files are purged from the IPUMS cache.
Importantly, if an extract's data and syntax files have been purged, the extract is still 
considered to have been completed, and `extract_status()` will return "complete."

.. code:: python

    # extract number 1 has been purged
    ipums.extract_status(collection="usa", extract="1")

returns:

.. code:: python

    'complete'

To check to see if an extract has been purged: 

.. code:: python

    ipums.extract_was_purged(collection="usa", extract="1")


returns:

.. code:: python

    True

For extracts that have had their files purged, the data collection name and extract ID 
number can be used to resubmit your old extract. Note that resubmitting a purged extract
results in a new extract with its own unique ID number!

.. code:: python

    resubmitted_extract = ipums.resubmit_purged_extract(collection="usa", extract="1")

    resubmitted_extract.extract_id

returns:

.. code:: python

    2





