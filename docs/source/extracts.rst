.. extracts

.. currentmodule:: ipumspy

IPUMS Extracts
==============

IPUMS-py can be used to read extracts made via the IPUMS web interface into python. This page discusses how to request an IPUMS extract via API using IPUMS-py. 

Extract Definition
------------------

An extract is defined by:

1. A data collection name
2. A list of IPUMS sample IDs from that collection
3. A list of IPUMS variable names from that collection

IPUMS metadata is not currently accessible via API. 
Sample IDs and IPUMS variable names can be browsed via the data collection's website. 
See the table below for data collection abreviations and links to sample IDs and variable browsing.
Note that not all IPUMS data collections are currently available via API. The table below will be
filled in as new IPUMS data collections become accessible via API.

.. list-table:: IPUMS data collections metadata resources
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

Each IPUMS data collection that is accessible via API (currently just IPUMS USA) has its own extract class.
Using this class to create your extract object obviates the need to specify a data collection.

For example:

.. code:: python

    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
    )

instantiates a UsaExtract object for the IPUMS USA data collection that includes the us2012b (2012 PRCS) sample, and the variables AGE and SEX.

Users also have the option to specify a data format and an extract description when creating an extract object.

.. code:: python

    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
        data_format="csv",
        description="My first IPUMS USA extract!"
    )

Once an extract object has been created, the extract must be submitted to the API.

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

Once an extract has been submitted, an extract ID number will be assigned to it.

.. code:: python

    extract.extract_id

returns the extract id number assigned by the IPUMS extract system. In the case of your first extract, this code will return

.. code:: python

    1

You can use this extract ID number along with the data collection name to check on or download 
your extract later if you lose track of the original extract object.

Extract status
--------------

After your extract has been submitted, you can check its status using 

.. code:: python

    ipums.extract_status(extract)

returns:

.. code:: python

    'started'

While IPUMS retains all of a user's extract definitions, after a certain period, the extract data and syntax files are purged from the IPUMS cache. Importantly, if an extract's data and syntax files have been purged, the extract is still considered to have been completed, and :meth:`.extract_status()` will return "completed."

.. code:: python

    # extract number 1 has been purged
    ipums.extract_status(collection="usa", extract="1")

returns:

.. code:: python

    'completed'

If an extract has been purged: 

.. code:: python

    ipums.extract_was_purged(collection="usa", extract="1")


returns:

.. code:: python

    True

For extracts that have had their files purged, the data collection name and extract ID number can be used to resubmit the old extract. Note that resubmitting a purged extract results in a new extract with its own unique ID number!

.. code:: python

    resubmitted_extract = ipums.resubmit_purged_extract(collection="usa", extract="1")

    resubmitted_extract.extract_id

returns:

.. code:: python

    2

Unsupported Features
--------------------

Not IPUMS extract features are currently supported for extracts made via API. 
For a list of currently unsupported features, see the developer documentation `here <https://beta.developer.ipums.org/docs/apiprogram/apis/usa/>`__.
This list will be updated as more features become available.



