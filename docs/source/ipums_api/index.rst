.. api_client_tools

.. currentmodule:: ipumspy

IPUMS API Client Tools
======================

``ipumspy`` provides a framework for users to submit extract requests and download IPUMS data via the IPUMS API.

IPUMS API Assets
----------------

The IPUMS API provides two asset types:

-   **IPUMS extract** endpoints can be used to submit extract requests for processing and download completed extract files.
-   **IPUMS metadata** endpoints can be used to discover and explore available IPUMS data as well as retrieve codes, names, 
    and other extract parameters necessary to form extract requests.

Supported IPUMS Collections
---------------------------

Furthermore, IPUMS consists of multiple *collections* that provide different data products. 
These collections fall into one of two categories:

-  **Microdata** collections distribute data for individual survey units, like people or households.
-  **Aggregate data** collections distribute summary tables of aggregate statistics for particular
   geographic units, and may also provide corresponding GIS mapping files.

Not all IPUMS collections are currently supported by the IPUMS API. The table below summarizes the 
available features for all collections currently supported by the API:

.. _collection support table:

.. list-table:: IPUMS Data Collections
    :widths: 20 20 20 20 20
    :header-rows: 1
    :align: center

    * - IPUMS data collection
      - Data Type
      - Collection ID
      - Request & download data
      - Browse metadata
    * - `IPUMS USA <https://usa.ipums.org/usa/>`__
      - Microdata
      - ``usa``
      - X
      - 
    * - `IPUMS CPS <https://cps.ipums.org/cps/>`__
      - Microdata
      - ``cps``
      - X
      - 
    * - `IPUMS International <https://international.ipums.org/international/>`__
      - Microdata
      - ``ipumsi``
      - X
      - 
    * - `IPUMS ATUS <https://www.atusdata.org/atus/>`__
      - Microdata
      - ``atus``
      - X
      - 
    * - `IPUMS AHTUS <https://www.ahtusdata.org/ahtus/>`__
      - Microdata
      - ``ahtus``
      - X
      - 
    * - `IPUMS MTUS <https://www.mtusdata.org/mtus/>`__
      - Microdata
      - ``mtus``
      - X
      - 
    * - `IPUMS NHIS <https://nhis.ipums.org/nhis/>`__
      - Microdata
      - ``nhis``
      - X
      - 
    * - `IPUMS MEPS <https://meps.ipums.org/meps/>`__
      - Microdata
      - ``meps``
      - X
      - 
    * - `IPUMS NHGIS <https://nhgis.org/>`__
      - Aggregate data
      - ``nhgis``
      - X
      - X

Note that ``ipumspy`` may not necessarily support all the functionality currently supported by
the IPUMS API. See the `API documentation <https://developer.ipums.org/>`__ for more information 
about its latest features.

Get an API Key
--------------

To interact with the IPUMS API, you'll need to register for access with the IPUMS project you'll be 
using. If you have not yet registered, you can find the link to register for each 
project at the top of its website, which can be accessed from `<https://ipums.org>`__.

Once you're registered, you'll be able to create an `API key <https://account.ipums.org/api_keys>`__.

For security reasons, we recommend that you store your IPUMS API key in an environment variable
rather than including it in your code:

.. code:: python

    import os
    os.environ["IPUMS_API_KEY"] = "<insert-your-api-key-here>"

Extract Objects
---------------

IPUMS extract requests can be constructed and submitted to the IPUMS API using either
the :class:`ipumspy.api.extract.MicrodataExtract` class (for microdata collections) or the
:class:`ipumspy.api.extract.AggregateDataExtract` class (for aggregate data collections).

See the documentation for each collection type for detailed instructions for building an extract
request:

- :doc:`Microdata collections<ipums_api_micro/micro_extracts>`
- :doc:`Aggregate data collections<ipums_api_aggregate/agg_extracts>`

.. toctree::
   :hidden:

   ipums_api_micro/index
   ipums_api_aggregate/index
