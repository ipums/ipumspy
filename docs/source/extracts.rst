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

IPUMS metadata is not currently accessible via API. Sample IDs and IPUMS variable names can be browsed via the data collection's website. See the table below for data collection abreviations and links to sample IDs and variable browsing. Note that not all IPUMS data collections are currently available via API. The table below will be
filled in as new IPUMS data collections become accessible via API.

.. _collection availability table:

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
      - `usa samples <https://usa.ipums.org/usa-action/samples/sample_ids>`__
      - `usa variables <https://usa.ipums.org/usa-action/variables/group>`__
    * - IPUMS CPS
      - cps
      - `cps samples <https://cps.ipums.org/cps-action/samples/sample_ids>`__
      - `cps variables <https://cps.ipums.org/cps-action/variables/group>`__
    * - IPUMS International
      - ipumsi
      - `ipumsi samples <https://international.ipums.org/international-action/samples/sample_ids>`__
      - `ipumsi variables <https://international.ipums.org/international-action/variables/group>`__


Extract Objects
---------------

Each IPUMS data collection that is accessible via API has its own extract class. Using this class to create your extract object obviates the need to specify a data collection.

For example:

.. code:: python

    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
    )

instantiates a UsaExtract object for the IPUMS USA data collection that includes the us2012b (2012 PRCS) sample, and the variables AGE and SEX.

IPUMS extracts can be requested as rectangular or hierarchical files. The ``data_structure`` argument defaults to ``{"rectangular": {"on": "P"}}`` to request a rectangular, person-level extract. The code snippet below requests a hierarchical USA extract.

.. code:: python

    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
        data_structure={"hierarchical": {}}
    )

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

Extract Features
----------------

IPUMS Extract features can be added or updated before an extract request is submitted. This section demonstrates adding features to the following IPUMS CPS extract.

.. code:: python

    extract = CPSExtract(
        ["cps2022_03s"],
        ["AGE", "SEX", "RACE"],
    )

Attach Characteristics
~~~~~~~~~~~~~~~~~~~~~~

IPUMS allows users to create variables that reflect the characteristics of other household members. The example below uses the :meth:`.attach_characteristics()` method to attach the spouse's AGE value, creating a new variable called SEX_SP in the extract that will contain the age of a person's spouse if they have one and be 0 otherwise. The :meth:`.attach_characteristics()` method takes the name of the variable to attach and the household member whose values the new variable will include. Valid household members include "spouse", "mother", "father", and "head".

.. code:: python

    extract.attach_characteristics("SEX", ["spouse"])

The following would add variables for the RACE value of both parents:

.. code:: python

    extract.attach_characteristics("RACE", ["mother", "father"])

Select Cases
~~~~~~~~~~~~

IPUMS allows users to limit their extract based on values of included variables. The code below uses the :meth:`.select_cases()` to select only the female records in the example IPUMS CPS extract. This method takes a variable name and a list of values for that variable for which to include records in the extract. Note that the variable must be included in the IPUMS extract object in order to use this feature; also note that this feature is only available for categorical varaibles.

.. code:: python

    extract.select_cases("SEX", ["2"])

The :meth:`.select_cases()` method defaults to using "general" codes to select cases. Some variables also have detailed codes that can be used to select cases. Consider the following example extract of the 2021 ACS data from IPUMS USA:

.. code:: python

    extract = UsaExtract(
        ["us2021a"],
        ["AGE", "SEX", "RACE"]
    )

In IPUMS USA, the `RACE <https://usa.ipums.org/usa-action/variables/race#codes_section>`_ variable has both general and detailed codes. A user interested in respondents who identify themselves with two major race groups can use general codes:

.. code:: python

    extract.select_cases("RACE", ["8"])

A user interested in respondents who identify as both White and Asian can use detailed case selection to only include those chose White and another available Asian cateogry. To do this, in addition to specifying the correct detailed codes, set the `general` flag to `False`:

.. code:: python

    extract.select_cases("RACE", 
                         ["810", "811", "812", "813", "814", "815", "816", "818"], 
                         general=False)

Add Data Quality Flags
~~~~~~~~~~~~~~~~~~~~~~

Data quality flags can be added to an extract on a per-variable basis or for the entire extract. The CPS extract example above could be re-defined as follows in order to add all available data quality flags:

.. code:: python

    extract = CpsExtract(
        ["cps2022_03s"],
        ["AGE", "SEX", "RACE"],
        data_quality_flags=True
    )

This extract specification will add data quality flags for all variables in the variable list to the extract for which data quality flags exist in the sample(s) in the samples list.

Data quality flags can also be selected for specific variables using the :meth:`.add_data_quality_flags()` method.

.. code:: python

    # add the data quality flag for AGE to the extract
    extract.add_data_quality_flags("AGE")

    # note that this method will also accept a list!
    extract.add_data_quality_flags(["AGE", "SEX"])

.. _Using Variable Objects to Include Extract Features:

Using Variable Objects to Include Extract Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is also possible to define all variable-level extract features when the IPUMS extract object is first defined using :class:`ipumspy.api.extract.Variable` objects. The example below defines an IPUMS CPS extract that includes a variable for the age of the spouse (``attached_characteristics``), limits the sample to women (``case_selections``), and includes the data quality flag for RACE (``data_quality_flags``).

.. code:: python

    fancy_extract = CpsExtract(
        ["cps2022_03s"],
        [
            Variable(name="AGE",
                     attached_characteristics=["spouse"]),
            Variable(name="SEX",
                     case_selections={"general": ["2"]}),
            Variable(name="RACE",
                     data_quality_flags=True)
         ]
    )

Unsupported Features
--------------------

Not all features available through the IPUMS extract web UI are currently supported for extracts made via API. 
For a list of currently unsupported features, see `the developer documentation <https://beta.developer.ipums.org/docs/apiprogram/apis/>`__.
This list will be updated as more features become available.



