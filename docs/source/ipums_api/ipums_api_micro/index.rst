.. ipumspy documentation for microdata extract objects

.. currentmodule:: ipumspy

Microdata Extracts
==================

Extract Objects
---------------

Construct an extract for an IPUMS microdata collection using the 
:class:`MicrodataExtract<ipumspy.api.extract.MicrodataExtract>` class.
At a minimum, any ``MicrodataExtract`` must contain:

1. An IPUMS collection ID
2. A list of sample IDs
3. A list of variable names.

We also recommend providing an extract description to make it easier to 
:ref:`identify and retrieve <extract-histories>` your extract in the future.

For example:

.. code:: python

    extract = MicrodataExtract(
        "usa",
        ["us2012b"],
        ["AGE", "SEX"],
        description="An IPUMS extract example"
    )

This instantiates a ``MicrodataExtract`` object for the `IPUMS USA <https://usa.ipums.org/usa/>`__ 
data collection that includes the us2012b (2012 PRCS) sample, and the variables AGE and SEX.

After instantiation, a ``MicrodataExtract`` object can be submitted to the API for processing
and downloaded as described on the :doc:`IPUMS API page<../../ipums_api/index>`.

Data Structures
---------------

IPUMS microdata extracts can be requested in rectangular, hierarhical, or household-only structures.

- Rectangular data combine data for different record types into single records in the output. 
  For instance, rectangular-on-person data provide person-level records with all requested household
  information attached to the persons in that household.
- Hierarchical data contain separate records for different record types.
- Household-only data contain household records without any person records.

The ``data_structure`` argument defaults to ``{"rectangular": {"on": "P"}}``, which requests a 
rectangular, person-level extract. The code snippet below requests a hierarchical USA extract 
instead:

.. code:: python

    extract = MicrodataExtract(
        "usa",
        ["us2012b"],
        ["AGE", "SEX"],
        description="An IPUMS extract example",
        data_structure={"hierarchical": {}},
    )

Some IPUMS data collections offer rectangular files on non-person record types. For example, IPUMS 
ATUS offers rectangular files at the activity level and IPUMS MEPS offers rectangular files at the 
round level. 

To rectangularize on a different record type, adjust the ``"on"`` key. For instance, to rectangularize
an IPUMS MEPS extract on round records:

.. code:: python

    extract = MicrodataExtract(
        "meps",
        ["mp2016"],
        ["AGE", "SEX", "PREGNTRD"],
        description="An IPUMS extract example",
        data_structure={"rectangular": {"on": "R"}},
    )

The table below shows the available data structures and the IPUMS data collections for which each is valid.

.. _collection data structures table:

.. list-table:: IPUMS data structures
    :widths: 23 40 18
    :header-rows: 1
    :align: center

    * - Data structure
      - Syntax
      - Collections 
    * - rectangular on Person (default)
      - ``data_structure={"rectangular": {"on": "P"}}``
      - all IPUMS microdata collections
    * - hierarchical
      - ``data_structure={"hierarchical": {}}``
      - all IPUMS microdata collections
    * - rectangular on Activity
      - ``data_structure={"rectangular": {"on": "A"}}``
      - ``atus``, ``ahtus``, ``mtus``
    * - rectangular on Round
      - ``data_structure={"rectangular": {"on": "R"}}``
      - ``meps``
    * - rectangular on Injury
      - ``data_structure={"rectangular": {"on": "I"}}``
      - ``nhis``
    * - household only
      - ``data_structure={"householdOnly": {}}``
      - ``usa``
    
Note that some types of records are only available as part of hierarchical extracts. This is true of 
IPUMS ATUS "Who" and "Eldercare"[*]_ records and of IPUMS MEPS "Event", "Condition", and "Prescription Medications" 
record types.

Users also have the option to specify a desired file format when creating an extract object
by using the ``data_format`` argument:

.. code:: python

    extract = MicrodataExtract(
        "usa",
        ["us2012b"],
        ["AGE", "SEX"],
        description="An IPUMS extract example",
        data_format="csv",
    )

.. _extract-features:

Extract Features
----------------

Certain features of a :class:`MicrodataExtract<ipumspy.api.extract.MicrodataExtract>` can be 
added or updated before an extract request is submitted. This section 
demonstrates adding features to the following IPUMS CPS extract.

.. code:: python

    extract = MicrodataExtract(
        "cps",
        ["cps2022_03s"],
        ["AGE", "SEX", "RACE"],
        description="A CPS extract example"
    )

Attach Characteristics
~~~~~~~~~~~~~~~~~~~~~~

IPUMS allows users to create variables that reflect the characteristics of other household 
members. The example below uses the :meth:`.attach_characteristics()` method to attach the 
spouse's AGE value, creating a new variable called SEX_SP in the extract that will contain the 
age of a person's spouse if they have one and be 0 otherwise. 

The :meth:`.attach_characteristics()` method takes the name of the variable to attach and the 
household member whose values the new variable will include. Valid household members 
include "spouse", "mother", "father", and "head".

.. code:: python

    extract.attach_characteristics("SEX", ["spouse"])

The following would add variables for the RACE value of both parents:

.. code:: python

    extract.attach_characteristics("RACE", ["mother", "father"])

Select Cases
~~~~~~~~~~~~

IPUMS allows users to restrict the records included in their extract based on values of included 
variables. In ``ipumspy``, use :meth:`.select_cases` to do so. This method takes a variable name and
a list of values for that variable. The resulting extract will only include the records whose data
for that variable match the indicated values.

For instance, the code below selects only the female records (code ``"2"``) in our example 
IPUMS CPS extract. 

.. code:: python

    extract.select_cases("SEX", ["2"])

.. note::
    The :meth:`.select_cases` can only be used with categorical variables, and the indictated
    variables must already be present in the IPUMS extract object.

Detailed Codes
**************

The :meth:`.select_cases()` method defaults to using *general* codes to select cases. Some 
variables also have *detailed* codes that can be used to select cases. Consider the following
example extract of the 2021 ACS data from IPUMS USA:

.. code:: python

    extract = MicrodataExtract(
        "usa",
        ["us2021a"],
        ["AGE", "SEX", "RACE"],
        description="Case selection example"
    )

In IPUMS USA, the `RACE <https://usa.ipums.org/usa-action/variables/race#codes_section>`_ variable has 
both general and detailed codes. A user interested in respondents who belong to
a general category, like "Two major races", can use general codes:

.. code:: python

    # Select persons identifying as "Two major races"
    extract.select_cases("RACE", ["8"])

However, to identify respondents belonging to more specific categories, you would need
to use detailed codes instead. For instance, to identify respondents who identify as both
White and Asian, you can use the detailed codes representing the intersection of White
and each of the other Asian response options (e.g. Chinese, Japanese, etc.).

To do this, in addition to specifying the correct detailed codes, set the ``general`` 
flag to ``False``:

.. code:: python

    extract.select_cases("RACE", 
                         ["810", "811", "812", "813", "814", "815", "816", "818"], 
                         general=False)

By default, case selection restricts the data to those *individuals* who
match the provided values for the indicated variables. Alternatively, you can create 
an extract that includes *all* the individuals in households that contain at least one individual 
who matches the case selection criteria. To do so, set the ``case_select_who`` flag to 
``"households"`` when instantiating the extract object. 

.. code:: python

    extract = MicrodataExtract(
        "usa",
        ["us2021a"],
        ["AGE", "SEX", "RACE"],
        description="Case selection example",
        case_select_who = "households"
    )

    extract.select_cases("RACE", 
                         ["810", "811", "812", "813", "814", "815", "816", "818"], 
                         general=False)

Add Data Quality Flags
~~~~~~~~~~~~~~~~~~~~~~

Some IPUMS variables have been edited for missing, illegible, and inconsistent values. 
Data quality flags indicate which values are edited or allocated.

Data quality flags can be added to an extract for individual variables or for the entire extract. 
The CPS extract example above could be re-defined as follows in order to add all available 
data quality flags:

.. code:: python

    extract = MicrodataExtract(
        "cps",
        ["cps2022_03s"],
        ["AGE", "SEX", "RACE"],
        data_quality_flags=True
    )

This extract specification will add data quality flags for all of the extract's
variables, provided that the data quality flags exist in the extract's sample(s).

Data quality flags can also be selected for specific variables using the :meth:`.add_data_quality_flags()` method.

.. code:: python

    # add the data quality flag for AGE to the extract
    extract.add_data_quality_flags("AGE")

    # note that this method will also accept a list!
    extract.add_data_quality_flags(["AGE", "SEX"])

.. _Using Variable Objects to Include Extract Features:

Variable Objects
~~~~~~~~~~~~~~~~

It is also possible to specify variable-level extract features when 
defining a :class:`MicrodataExtract<ipumspy.api.extract.MicrodataExtract>` using 
:class:`Variable<ipumspy.api.extract.Variable>` objects. 

The example below defines an IPUMS CPS extract that includes a variable for the age of 
the spouse (``attached_characteristics``), limits the sample to women (``case_selections``), and includes the 
data quality flag for RACE (``data_quality_flags``).

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
         ],
         description="A fancy CPS extract",
    )

Time Use Variables
------------------

The IPUMS Time Use collections (ATUS, AHTUS, and MTUS) offer a special type of variable called 
time use variables. These variables record to the number of minutes a respondent spent during 
the 24-hour reference period on activities that match specific criteria. Time use variables
come in two different types:

- **System** time use variables have been pre-made by IPUMS based on common definitions of activities.
- **User-defined** time use variables can be constructed by users based on their own criteria using
  the IPUMS web interface.

Currently time use variable *creation* is not supported via the IPUMS API. 
However, users can use the IPUMS API to *request* system time use variables as well as their 
own custom user-defined time use variables that they have previously created in the IPUMS 
web interface and saved to their user account.

Because time use variables are a special type of variable, they need to be requested 
using the ``time_use_variables`` argument specifically and cannot be added to 
the ``variables`` argument list alongside standard variables. Below is an example 
of an IPUMS ATUS extract that contains variables AGE and SEX as well as the system 
time use variable BLS_PCARE:

.. code:: python

    atus_extract = MicrodataExtract(
        collection="atus",
        samples=["at2016"],
        variables=["AGE", "SEX"],
        time_use_variables=["BLS_PCARE"],
        description="An time use variable example"
    )

Like other variables, time use variables can also be passed to 
:class:`MicrodataExtract<ipumspy.api.extract.MicrodataExtract>` as a list of 
:class:`TimeUseVariable<ipumspy.api.extract.TimeUseVariable>` objects.

These objects are useful when requesting user-defined time use variables, as you must 
specify the ``owner`` field, which must contain the email associated with your IPUMS account:

.. code:: python

    atus_extract = MicrodataExtract(
        collection="atus",
        samples=["at2016"],
        variables=["AGE", "SEX"],
        time_use_variables=[
            TimeUseVariable(name="BLS_PCARE"), 
            TimeUseVariable(name="MY_CUSTOM_TUV", owner="newipumsuser@gmail.com")
        ],
        description="User-defined time use variable example"
    )

IPUMS ATUS Sample Members
-------------------------

Though time use information is only available for designated respondents in IPUMS ATUS, users 
may also wish to include household members of these respondents and/or non-respondents in 
their IPUMS ATUS extracts. These "sample members" can be included by using the ``sample_members`` 
keyword argument. The example below includes both household members of ATUS respondents and 
non-respondents alongside ATUS respondents (included by default).

.. code-block:: python

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
        },
        description="Sample members example"
    )

Unsupported Extract Features
----------------------------

.. warning::

    Not all features available through the IPUMS extract web UI are currently supported for extracts made via API. 
    For a list of supported and unsupported features for each IPUMS data collection, see 
    `the developer documentation <https://developer.ipums.org/docs/v2/apiprogram/apis/microdata/>`__.
    This list will be updated as more features become available.

.. rubric:: Notes

.. [*] Note that IPUMS ATUS Eldercare records will be included in a hierarchical extract automatically if 
    Eldercare variables are selected. There is no API equivalent to the "include eldercare" checkbox 
    in the Extract Data Structure menu in the IPUMS ATUS web interface.
    