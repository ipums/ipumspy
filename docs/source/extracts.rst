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
    * - `IPUMS USA <https://usa.ipums.org/usa/>`__
      - usa
      - `usa samples <https://usa.ipums.org/usa-action/samples/sample_ids>`__
      - `usa variables <https://usa.ipums.org/usa-action/variables/group>`__
    * - `IPUMS CPS <https://cps.ipums.org/cps/>`__
      - cps
      - `cps samples <https://cps.ipums.org/cps-action/samples/sample_ids>`__
      - `cps variables <https://cps.ipums.org/cps-action/variables/group>`__
    * - `IPUMS International <https://international.ipums.org/international/>`__
      - ipumsi
      - `ipumsi samples <https://international.ipums.org/international-action/samples/sample_ids>`__
      - `ipumsi variables <https://international.ipums.org/international-action/variables/group>`__
    * - `IPUMS ATUS <https://www.atusdata.org/atus/>`__
      - atus
      - `atus samples <https://www.atusdata.org/atus-action/samples/sample_ids>`__
      - `atus variables <https://www.atusdata.org/atus-action/variables/group>`__
    * - `IPUMS AHTUS <https://www.ahtusdata.org/ahtus/>`__
      - ahtus
      - `ahtus samples <https://www.ahtusdata.org/ahtus-action/samples/sample_ids>`__
      - `ahtus variables <https://www.ahtusdata.org/ahtus-action/variables/group>`__
    * - `IPUMS MTUS <https://www.mtusdata.org/mtus/>`__
      - mtus
      - `mtus samples <https://www.mtusdata.org/mtus-action/samples/sample_ids>`__
      - `mtus variables <https://www.mtusdata.org/mtus-action/variables/group>`__
    * - `IPUMS NHIS <https://nhis.ipums.org/nhis/>`__
      - nhis
      - `nhis samples <https://nhis.ipums.org/nhis-action/samples/sample_ids>`__
      - `nhis variables <https://nhis.ipums.org/nhis-action/variables/group>`__
    * - `IPUMS MEPS <https://meps.ipums.org/meps/>`__
      - meps
      - `meps samples <https://meps.ipums.org/meps-action/samples/sample_ids>`__
      - `meps variables <https://meps.ipums.org/meps-action/variables/group>`__


Extract Objects
---------------

All IPUMS data collection currently supported by `ipumspy` are microdata collections; extracts for these data collections can be constructed and submitted to the IPUMS API using the :class:`ipumspy.api.extract.MicrodataExtract` class. The minimum required arguments are 1) an IPUMS collection id, 2) a list of sample ids, and 3) a list of variable names.

For example:

.. code:: python

    extract = MicrodataExtract(
        "usa",
        ["us2012b"],
        ["AGE", "SEX"],
    )

instantiates a MicrodataExtract object for the IPUMS USA data collection that includes the us2012b (2012 PRCS) sample, and the variables AGE and SEX.

IPUMS extracts can be requested as rectangular or hierarchical files. The ``data_structure`` argument defaults to ``{"rectangular": {"on": "P"}}`` to request a rectangular, person-level extract. The code snippet below requests a hierarchical USA extract.

.. code:: python

    extract = MicrodataExtract(
        "usa",
        ["us2012b"],
        ["AGE", "SEX"],
        data_structure={"hierarchical": {}}
    )


Some IPUMS data collections offer rectangular files on non-person record types. For example, IPUMS ATUS offers rectangular files at the activity level and IPUMS MEPS offers rectangular files at the round level. Below is an example of an IPUMS MEPS extract object that is rectanularized on round.

.. code:: python

    extract = MicrodataExtract(
        "meps",
        ["mp2016"],
        ["AGE", "SEX", "PREGNTRD"],
        data_structure={"rectangular": {"on": "R"}}
    )

The table below shows the available data structures and the IPUMS data collections for which each is valid.

.. _collection data structures table:

.. list-table:: IPUMS data structures
    :widths: 23 40 18
    :header-rows: 1
    :align: center

    * - data structure
      - syntax
      - collections 
    * - rectangular on Person (default)
      - ``data_structure={"rectangular": {"on": "P"}}``
      - all IPUMS microdata collections
    * - hierarchical
      - ``data_structure={"hierarchical": {}}``
      - all IPUMS microdata collections
    * - rectangular on Activity
      - ``data_structure={"rectangular": {"on": "A"}}``
      - atus, ahtus, mtus
    * - rectangular on Round
      - ``data_structure={"rectangular": {"on": "R"}}``
      - meps
    * - rectangular on Injury
      - ``data_structure={"rectangular": {"on": "R"}}``
      - nhis
    * - household only
      - ``data_structure={"householdOnly": {}}``
      - usa
    
Note that some types of records are only available as part of hierarchical extracts. This is true of IPUMS ATUS "Who" and "Eldercare" [*]_ records and of IPUMS MEPS "Event", "Condition", and "Prescription Medications" record types.
    
Users also have the option to specify a data format and an extract description when creating an extract object.

.. code:: python

    extract = MicrodataExtract(
        "usa",
        ["us2012b"],
        ["AGE", "SEX"],
        data_format="csv",
        description="My first IPUMS USA extract!"
    )



Once an extract object has been created, the extract must be submitted to the API.

.. code:: python

    from ipumspy import IpumsApiClient, MicrodataExtract

    IPUMS_API_KEY = your_api_key
    DOWNLOAD_DIR = Path(your_download_dir)

    ipums = IpumsApiClient(IPUMS_API_KEY)

    # define your extract
    extract = MicrodataExtract(
        "usa",
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

While IPUMS retains all of a user's extract definitions, after a certain period, the extract data and syntax files are purged from the IPUMS cache - these extracts are said to be "expired". Importantly, if an extract's data and syntax files have been removed, the extract is still considered to have been completed, and :meth:`.extract_status()` will return "completed."

.. code:: python

    # extract number 1 has expired
    ipums.extract_status(collection="usa", extract="1")

returns:

.. code:: python

    'completed'

If an extract has expired: 

.. code:: python

    ipums.extract_is_expired(collection="usa", extract="1")


returns:

.. code:: python

    True

For extracts that have expired, the data collection name and extract ID number can be used to re-create and re-submit the old extract. **Note that re-creating and re-submitting a expired extract results in a new extract with its own unique ID number!**

.. code:: python

    # create a UsaExtract object from the expired extract definition
    renewed_extract = ipums.get_extract_by_id(collection="usa", extract_id=1)

    # submit the renewed extract to re-generate the data and syntax files
    resubmitted_extract = ipums.submit_extract(renewed_extract)

    resubmitted_extract.extract_id

returns:

.. code:: python

    2

Extract Features
----------------

IPUMS Extract features can be added or updated before an extract request is submitted. This section demonstrates adding features to the following IPUMS CPS extract.

.. code:: python

    extract = MicrodataExtract(
        "cps",
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

    extract = MicrodataExtract(
        "usa",
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

By default, case selection includes only individuals with the specified values for the specified variables. In the previous example, only persons who identified as both White and Asian are included in the extract. To make an extract that contains individuals in households that include an individual who identifies as both White and Asian, set the ``case_select_who`` flag to ``"households"`` when instantiating the extract object. The code snippet below creates such an extract. Note that whether to select individuals or households must be specified at the extract level, while what values to select on and whether these values are general or detailed codes is specified at the variable level.

.. code:: python

    extract = MicrodataExtract(
        "usa",
        ["us2021a"],
        ["AGE", "SEX", "RACE"],
        case_select_who = "households"
    )
    extract.select_cases("RACE", 
                         ["810", "811", "812", "813", "814", "815", "816", "818"], 
                         general=False)



Add Data Quality Flags
~~~~~~~~~~~~~~~~~~~~~~

Data quality flags can be added to an extract on a per-variable basis or for the entire extract. The CPS extract example above could be re-defined as follows in order to add all available data quality flags:

.. code:: python

    extract = MicrodataExtract(
        "cps",
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

    fancy_extract = MicrodataExtract(
        "cps",
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

Time Use Variables
------------------
The IPUMS Time Use collections (ATUS, AHTUS, and MTUS) offer a special type of variable called time use variables. These variables correspond to the number of minutes a respondent spent during the 24-hour reference period on activities that match specific criteria. Within time use variables, there are two different variable types: "system" time use variables that IPUMS offers pre-made for users based on common definitions of activities and "user-defined" time use variables that users can construct based on their own criteria using the IPUMS web interface for these collections. Currently time use variable creation is not supported via the IPUMS API. However, users can request system time use variables as well as their own custom user-defined time use variables that they have previously created in the IPUMS web interface and saved to their user account via the IPUMS API.

Because time use variables are a special type of variable, they need to be requested as time use variables specifically and cannot be added to the `varibles` argument list with non-time use variables. Below is an example of an IPUMS ATUS extract that contains variables AGE and SEX as well as the system time use variable BLS_PCARE.

.. code:: python

    atus_extract = MicrodataExtract(
        collection="atus",
        samples=["at2016"],
        variables=["AGE", "SEX"],
        time_use_variables=["BLS_PCARE"]
    )

Like other variables, time use variables can also be passed to `MicrodataExtract` as a list of `TimeUseVariable` objects.

.. code:: python

    atus_extract = MicrodataExtract(
        collection="atus",
        samples=["at2016"],
        variables=["AGE", "SEX"],
        time_use_variables=[TimeUseVariable(name="BLS_PCARE")]
    )

This approach may be simpler when including user-defined timeuse variables in your extract, as user-defined time use variables also have an owner attribute that must be specified. The owner field contains the email address associated with your IPUMS account.

.. code:: python

    atus_extract = MicrodataExtract(
        collection="atus",
        samples=["at2016"],
        variables=["AGE", "SEX"],
        time_use_variables=[
            TimeUseVariable(name="BLS_PCARE"), 
            TimeUseVariable(name="MY_CUSTOM_TUV", owner="newipumsuser@gmail.com")
        ]
    )

IPUMS ATUS Sample Members
-------------------------

Though time use information is only available for designated respondents in IPUMS ATUS, users may also wish to include household members of these respondents and/or non-respondents in their IPUMS ATUS extracts. These "sample members" can be included by using the ``sample_members`` key word argument. The example below includes both household members of ATUS respondents and non-respondents alongside ATUS respondents (included by default).

.. code:: python

    atus_extract = MicrodataExtract(
        collection="atus",
        samples=["at2016"],
        variables=["AGE", "SEX"],
        time_use_variables=[
            TimeUseVariable(name="BLS_PCARE"), 
            TimeUseVariable(name="MY_CUSTOM_TUV", owner="newipumsuser@gmail.com")
        ],
        sample_members={
            "include_non_respondents": True,
            "include_household_members": True
        }
    )

Unsupported Extract Features
----------------------------

Not all features available through the IPUMS extract web UI are currently supported for extracts made via API. 
For a list of supported and unsupported features for each IPUMS data collection, see `the developer documentation <https://developer.ipums.org/docs/v2/apiprogram/apis/microdata/>`__.
This list will be updated as more features become available.

Extract Histories
-----------------
``ipumspy`` offers several ways to peruse your extract history for a given IPUMS data collection.

:meth:`.get_previous_extracts()` can be used to retrieve your 10 most recent extracts for a given collection. The limit can be set to a custom n of most recent previous extracts.

.. code:: python
    
    from ipumspy import IpumsApiClient

    ipums = IpumsApiClient("YOUR_API_KEY")

    # get my 10 most-recent USA extracts
    recent_extracts = ipums.get_previous_extracts("usa")

    # get my 20 most-recent CPS extracts
    more_recent_extracts = ipums.get_previous_extracts("cps", limit=20)

The :meth:`.get_extract_history()` generator makes it easy to filter your extract history to pull out extracts with certain variables, samples, features, file formats, etc. By default, this generator returns pages extract definitions of the maximum possible size, 500. Page size can be set to a lower number using the ``page_size`` argument.

.. code:: python

    # make a list of all of my extracts from IPUMS CPS that include the variable STATEFIP
    extracts_with_state = []
    # get pages with 50 CPS extracts per page
    for page in ipums.get_extract_history("cps", page_size=100):
        for ext in page["data"]:
            extract_obj = MicrodataExtract(**ext["extractDefinition"])
            if "STATEFIP" in [var.name for var in extract_obj.variables]:
                extracts_with_state.append(extract_obj)


.. [*] Note that IPUMS ATUS Eldercare records will be included in a hierarchical extract automatically if Eldercare variables are selected. There is no API equivalent to the "include eldercare" checkbox in the Extract Data Structure menue in the IPUMS ATUS web interface.