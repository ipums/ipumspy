.. ipumspy documentation for working with IPUMS variables

.. currentmodule:: ipumspy

IPUMS variables
===============

IPUMS Variable Objects
----------------------

A list of user-defined :class:`ipumspy.api.extract.Variable` objects can be passed to the IPUMS Extract classes to build extracts that take advantage of available IPUMS extract features. For more information on using IPUMS extract features in `ipumspy`, see :ref:`Using Variable Objects to Include Extract Features` for more information.

IPUMS Variable Metadata
-----------------------

Currently, IPUMS metadata is not accessible via API and all variable information is pulled from an extract's DDI codebook. This codebook is created after the extract is submitted to the IPUMS extract system.

Variable Descriptions
*********************

The :class:`ipumspy.ddi.VariableDescription` objects built from the ddi codebook provide easy access to variable metadata. These can be returned using the :meth:`.get_variable_info()` method.

.. code:: python

    from ipumspy import readers

    # read ddi and data
    ddi_codebook = readers.read_ipums_ddi(path/to/ddi/xml/file)
    ipums_df = readers.read_microdata(ddi_codebook, path/to/data/file)

    # get VariableDescription for SEX
    sex_info = ddi_codebook.get_variable_info('SEX')

    # see codes and labels for SEX
    print(sex_info.codes)

    # see variable description for SEX
    print(sex_info.description)

The above code results in the following::

    # codes and labels
    {'Male': 1, 'Female': 2}

    # description
    'SEX reports whether the person was male or female.'

More on Value labels
********************

Users can filter on categorical variables using labels instead of numerical values
For example, the following code retains only the female respondents in ``ipums_df``.

.. code:: python

    # retrieve the VaribleDescription for the variable SEX
    sex_info = ddi_codebook.get_variable_info('SEX')
    women = ipums_df[ipums_df['SEX'] == sex_info.codes['Female']]

It is possible to filter on both categorical variables using labels and on numerical values.
The following retains only women over the age of 16 in ``ipums_df``

.. code:: python

    adult_women = ipums_df[(ipums_df['SEX'] == sex_info.codes['Female']) &
                           (ipums_df['AGE'] > 16)]