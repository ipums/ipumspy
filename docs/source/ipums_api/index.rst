.. api_client

.. currentmodule:: ipumspy

IPUMS API
=========

ipumspy provides a framework for users to submit extract requests and download IPUMS data via the IPUMS API.

API Assets
----------

The IPUMS API provides two asset types:

-   **IPUMS extract** endpoints can be used to submit extract requests for processing and download completed extract files.
-   **IPUMS metadata** endpoints can be used to discover and explore available IPUMS data as well as retrieve codes, names, 
    and other extract parameters necessary to form extract requests.

.. _supported collections:

Supported IPUMS Collections
---------------------------

IPUMS consists of multiple collections that provide different data products. 
These collections fall into one of two categories:

-  :doc:`Microdata<ipums_api_micro/index>` collections distribute data for individual survey units, like people or households.
-  :doc:`Aggregate data<ipums_api_aggregate/index>` collections distribute summary tables of aggregate statistics for particular
   geographic units, and may also provide corresponding GIS mapping files.

Not all IPUMS collections are currently supported by the IPUMS API. The table below summarizes the 
available features for all collections currently supported by the API:

.. _collection support table:

.. list-table:: Supported data collections
    :widths: 28 20 20 16 16
    :header-rows: 1
    :align: center

    * - IPUMS data collection
      - Data type
      - Collection ID
      - Request & download data
      - Browse metadata
    * - `IPUMS USA <https://usa.ipums.org/usa/>`__
      - Microdata
      - ``usa``
      - **X**
      - 
    * - `IPUMS CPS <https://cps.ipums.org/cps/>`__
      - Microdata
      - ``cps``
      - **X**
      - 
    * - `IPUMS International <https://international.ipums.org/international/>`__
      - Microdata
      - ``ipumsi``
      - **X**
      - 
    * - `IPUMS ATUS <https://www.atusdata.org/atus/>`__
      - Microdata
      - ``atus``
      - **X**
      - 
    * - `IPUMS AHTUS <https://www.ahtusdata.org/ahtus/>`__
      - Microdata
      - ``ahtus``
      - **X**
      - 
    * - `IPUMS MTUS <https://www.mtusdata.org/mtus/>`__
      - Microdata
      - ``mtus``
      - **X**
      - 
    * - `IPUMS NHIS <https://nhis.ipums.org/nhis/>`__
      - Microdata
      - ``nhis``
      - **X**
      - 
    * - `IPUMS MEPS <https://meps.ipums.org/meps/>`__
      - Microdata
      - ``meps``
      - **X**
      - 
    * - `IPUMS NHGIS <https://nhgis.org/>`__
      - Aggregate data
      - ``nhgis``
      - **X**
      - **X**
    * - `IPUMS IHGIS <https://ihgis.ipums.org/>`__
      - Aggregate data
      - ``ihgis``
      - **X**
      - **X**

Note that ipumspy may not necessarily support all the functionality currently supported by
the IPUMS API. See the `API documentation <https://developer.ipums.org/>`__ for more information 
about its latest features.

Get an API Key
--------------

Before you can interact with the IPUMS API, you'll need to make sure you've 
:ref:`obtained and set up <get an api key>` your API key.

You can then initialize an API client using your key. (The following assumes your 
key is stored in the ``IPUMS_API_KEY`` environment variable as described in the link above.)

.. code:: python

    import os
    from pathlib import Path
    from ipumspy import IpumsApiClient, MicrodataExtract, save_extract_as_json

    IPUMS_API_KEY = os.environ.get("IPUMS_API_KEY")

    ipums = IpumsApiClient(IPUMS_API_KEY)

Extract Objects
---------------

To request IPUMS data via the IPUMS API, you need to first create an extract request object,
which contains the parameters that define the content, format, and layout for the data you'd like
to download.

IPUMS extract requests can be constructed and submitted to the IPUMS API using either

- The :class:`MicrodataExtract<ipumspy.api.extract.MicrodataExtract>` class (for microdata collections)
- The :class:`AggregateDataExtract<ipumspy.api.extract.AggregateDataExtract>` class (for aggregate data collections)

For instance, the following defines a simple IPUMS USA extract request for the 
AGE, SEX, RACE, STATEFIP, and MARST variables from the 2018 and 2019 American Community Survey (ACS):

.. code:: python
    
    extract = MicrodataExtract(
        collection="usa",
        description="Sample USA extract",
        samples=["us2018a", "us2019a"],
        variables=["AGE", "SEX", "RACE", "STATEFIP", "MARST"],
    )

.. seealso::
  The available extract definition options vary across collections. See the 
  :doc:`microdata extracts<ipums_api_micro/index>` and :doc:`aggregate data extracts<ipums_api_aggregate/index>`
  pages for more information about the available extract parameters for each type.

.. _ipums-metadata:

IPUMS Metadata
--------------

Microdata Collections
*********************

Currently, comprehensive IPUMS API metadata is only available for IPUMS NHGIS.
For microdata collections, only sample information is available. You can obtain a dictionary 
of sample codes with :py:meth:`.get_all_sample_info`.

Aggregate Data Collections
**************************

You can use the IPUMS API metadata endpoints to identify the codes you can use to include
particular data sources in your extract request.

The IPUMS API provides access to two different types of metadata. The first provides a listing of all
available data sources of a given type (see the :ref:`table <metadata support table>` below for supported types). 
These records can be accessed with :py:meth:`.get_metadata_catalog`.

This method returns a generator of metadata pages, allowing you to iterate through and search for 
particular data sources. For instance, to identify all available IPUMS NHGIS data tables that
contain data referring to "Urban Population", we could do the following:

.. code:: python

  urb_dts = []

  # Identify all data tables referring to "Urban Population"
  for page in ipums.get_metadata_catalog("nhgis", metadata_type="data_tables"):
      for dt in page["data"]:
          if "Urban Population" in dt["description"]:
              urb_dts.append(dt)

The IPUMS API also provides access to detailed metadata about individual data sources. Request
this metadata by using an ``IpumsMetadata`` object to indicate the individual data source
for which to retrieve metadata. For instance, to request metadata for IPUMS NHGIS time series table "A00":

.. code:: python

  tst = TimeSeriesTableMetadata("nhgis", "A00")

Submit the request to the IPUMS API with :py:meth:`.get_metadata`. The returned object will contain the 
metadata obtained for the requested data source:

.. code:: python

  ipums.get_metadata(tst)

  tst.description
  #> 'Total Population'

The following table summarizes the currently available metadata endpoints. Endpoints listed
in the **Metadata type** column can be used with the indicated collection in :py:meth:`.get_metadata_catalog`.
Classes listed in the **Detailed metadata class** column can be used to obtain detailed metadata for
individual data sources of that type.

.. _metadata support table:

.. list-table:: Supported metadata endpoints
    :widths: 3 2 5
    :header-rows: 1
    :align: center

    * - Collection
      - Metadata type
      - Detailed metadata class
    * - NHGIS
      - ``datasets``
      - :py:class:`~ipumspy.api.metadata.NhgisDatasetMetadata`
    * - NHGIS
      - ``data_tables``
      - :py:class:`~ipumspy.api.metadata.NhgisDataTableMetadata`
    * - NHGIS
      - ``time_series_tables``
      - :py:class:`~ipumspy.api.metadata.TimeSeriesTableMetadata`
    * - NHGIS
      - ``shapefiles``
      -
    * -
      -
      -
    * - IHGIS
      - ``datasets``
      - :py:class:`~ipumspy.api.metadata.IhgisDatasetMetadata`
    * - IHGIS
      - ``data_tables``
      - :py:class:`~ipumspy.api.metadata.IhgisDataTableMetadata`
    * - IHGIS
      - ``tabulation_geographies``
      -

.. _submit-extract:

Submit an Extract Request
-------------------------

Once you've created an extract object, you can submit it to the IPUMS servers for processing:

.. code:: python
	
	ipums.submit_extract(extract)

If the extract is succesfully submitted, it will receive an ID number:

.. code:: python

	print(extract.extract_id)
	#> 1

You can use this extract ID number along with the data collection name to check on or 
download your extract later if you lose track of the original extract object.

Download an Extract
-------------------

It may take some time for the IPUMS servers to process your extract request. You can check the
current status of a request:

.. code:: python

	print(ipums.extract_status(extract))
	#> started

Instead of repeatedly checking the status, you can explicitly wait for the extract
to complete before attempting to download it:

.. code:: python

	ipums.wait_for_extract(extract)

At this point, you can safely download the extract:

.. code:: python

	DOWNLOAD_DIR = Path("<your_download_dir>")
	ipums.download_extract(extract, download_dir=DOWNLOAD_DIR)

Extract Status
--------------

If you lose track of the ``extract`` object for any reason, you may check the status
and download the extract using only the name of the ``collection`` and the ``extract_id``.

.. code:: python

    # Check the extract status
    extract_status = ipums.extract_status(extract=1, collection="usa")
    print(f"extract is {extract_status}")
    #> extract is started

You can also wait for and download an extract using this unique identifier:

.. code:: python

    ipums.wait_for_extract(extract=1, collection="usa")
    ipums.download_extract(extract=1, collection="usa")

Expired Extracts
****************

While IPUMS retains all of a user's extract definitions, after a certain period, the extract data and syntax 
files are purged from the IPUMS cache—these extracts are said to be "expired". Importantly, if an extract's data and 
syntax files have been removed, the extract is still considered to have been completed, and 
:meth:`.extract_status()` will return "completed."

.. code:: python
    
    # Extract number 1 has expired, but status listed as completed
    extract_status = ipums.extract_status(extract=1, collection="usa")
    
    print(extract_status)
    #> completed

You can confirm whether an extract has expired with the following:

.. code:: python
    
    is_expired = ipums.extract_is_expired(extract=1, collection="usa")

    print(is_expired)
    #> True

For extracts that have expired, the data collection name and extract ID number can be used to 
re-create and re-submit the old extract. 

.. attention::
	Note that re-creating and "re-submitting" an expired extract results in a **new** extract with its own unique ID number!

.. code:: python

    # Create a MicrodataExtract object from the expired extract definition
    renewed_extract = ipums.get_extract_by_id(collection="usa", extract_id=1)

    # Submit the renewed extract to re-generate the data and syntax files
    resubmitted_extract = ipums.submit_extract(renewed_extract)

    print(resubmitted_extract.extract_id)
    #> 2

Sharing Extract Definitions
---------------------------

ipumspy also makes it easier to share IPUMS extracts with collaborators.
By saving your extract as a standalone file, you can send it to other researchers
or reviewers, allowing them to generate an identical extract and download 
the same data used in your analysis. 

Collaborators submitting your extract definition will need to be registered with the 
data collection represented in the extract and have their own API key to succesfully 
submit the request. The request will be processed under their account, but the data in the resulting 
extract will be identical.

.. note::
    Sharing IPUMS extract definitions using files will ensure that your collaborators are able to submit the 
    same extract definition to the IPUMS extract system. However, IPUMS data are updated to fix errors as we 
    become aware of them and preserving extract definitions in a file do not insulate against these types of 
    changes to data. 
    
    In other words, if the IPUMS data included in the extract definition change between 
    submission of extracts based on this definition, the resulting downloaded files will not be identical. 
    IPUMS collections keep a log of errata and other changes on their websites.


Using JSON
**********

Use the following to save your extract object in JSON format:

.. code:: python

    save_extract_as_json(extract, filename="my_extract.json")

If you send this file to a collaborator, they can load it into ipumspy and submit it
themselves:

.. code:: python
    
    import os
    from ipumspy import IpumsApiClient, define_extract_from_json

    IPUMS_API_KEY = os.environ.get("IPUMS_API_KEY")
    ipums = IpumsApiClient(IPUMS_API_KEY)

    extract = define_extract_from_json("my_extract.json")
    ipums.submit_extract(extract)

.. _using-yaml:

Using YAML
**********

You can also store your extract in YAML format. For instance, to re-create
the extract we made above, we could save a file called ``ipums.yaml``
(for instance) with the following contents:

.. code:: yaml

    description: Sample USA extract
    collection: usa
    samples:
      - us2018a
      - us2019a
    variables:
      - AGE
      - SEX
      - RACE
      - STATEFIP
      - MARST

We can load the file into ipumspy by parsing the file into a dictionary
and then converting the dictionary to a
:class:`MicrodataExtract<ipumspy.api.extract.MicrodataExtract>` object.

.. code:: python

    import yaml
    from ipumspy import extract_from_dict

    with open("ipums.yaml") as infile:
        extract = extract_from_dict(yaml.safe_load(infile))

.. tip::
    You can also use the ipumspy :doc:`CLI<../cli>` to easily submit extract requests for
    definitions saved in YAML format.
    
.. _extract-histories:

Extract Histories
-----------------

ipumspy offers two ways to peruse your extract history for a given IPUMS data collection.

:meth:`.get_previous_extracts()` can be used to retrieve your most recent extracts for a 
given collection. By default, it retrieves your previous 10 extracts, but you can adjust
the ``limit`` argument to retrieve more or fewer records:

.. code:: python
    
    from ipumspy import IpumsApiClient

    ipums = IpumsApiClient("YOUR_API_KEY")

    # get my 10 most-recent USA extracts
    recent_extracts = ipums.get_previous_extracts("usa")

    # get my 20 most-recent CPS extracts
    more_recent_extracts = ipums.get_previous_extracts("cps", limit=20)

Alternatively, the :meth:`.get_extract_history()` generator makes it easy to filter your extract history to 
pull out extracts with certain features (e.g., variables, file formats, etc.). By default, this 
generator returns pages of extract definitions of the maximum possible size of 500 extract definitions 
per page. Page size can be set to a lower number using the ``page_size`` argument.

Here, we filter our history to identify all our CPS extracts containing the ``STATEFIP`` variable:

.. code:: python

    extracts_with_state = []

    # Get pages with 100 CPS extracts per page
    for page in ipums.get_extract_history("cps", page_size=100):
        for ext in page["data"]:
            extract_obj = extract_from_dict(ext["extractDefinition"])
            if "STATEFIP" in [var.name for var in extract_obj.variables]:
                extracts_with_state.append(extract_obj)

Browsing your extract history is a good way to identify previous extracts and re-submit them.

.. tip::
    Specifying a memorable extract ``description`` when defining an extract object
    can make it easier to identify the extract in your history in the future.

.. toctree::
   :hidden:

   ipums_api_micro/index
   ipums_api_aggregate/index
