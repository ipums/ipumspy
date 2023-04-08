:orphan: Supress Sphinx warning about this file not being in any toctree

.. ipumspy version history

Change Log
==========

All noteable changes to this project are documented on this page.
This project adheres to `Semantic Versioning`_.

.. _Semantic Versioning: http://semver.org/

0.3.0
-----
2023-04-08

* Breaking Changes
  
  * This release marks the beginning of support for IPUMS API version 2 and ipumspy no longer supports requests to version 1 or version beta of the IPUMS API. This means that extract definitions created and saved to files using previous versions of ipumspy can no longer be submitted as-is to the IPUMS API using this library! These definitions can be modified for use with v0.3.0 of ipumspy and IPUMS API version 2 by changing the ``data_format`` key to ``dataFormat`` and the ``data_structure`` key to ``dataStructure``. More information on `versioning of the IPUMS API <https://developer.ipums.org/docs/apiprogram/versioning/>`_ and `breaking changes in version 2 <https://developer.ipums.org/docs/apiprogram/changelog/>`_ can be found at the IPUMS developer portal.
  * The ``resubmit_purged_extract()`` method has been removed; use :py:meth:`~ipumspy.api.IpumsApiClient.submit_extract()` instead.
  * The ``extract_was_purged()`` method has been renamed to :py:meth:`~ipumspy.api.IpumsApiClient.extract_is_expired()`.
  * The ``CollectionInformation`` class has been removed. To retrieve information about available samples in a collection, use :py:meth:`~ipumspy.api.IpumsApiClient.get_all_sample_info()`
  * The ``define_extract_from_ddi()`` method has been removed.
  * The ``retrieve_previous_extracts()`` method has been renamed to :py:meth:`~ipumspy.api.IpumsApiClient.get_previous_extracts()`

* New Features

  * Support for IPUMS API version 2 features!

    * Added :py:meth:`~ipumspy.api.BaseExtract.attach_characteristics()`
    * Added :py:meth:`~ipumspy.api.BaseExtract.select_cases()`
    * Added :py:meth:`~ipumspy.api.BaseExtract.add_data_quality_flags()`
    * Added optional ``data_quality_flags`` keyword argument to IPUMS extract classes to include all available data quality flags for variables in the extract
    * Added optional ``select_case_who`` keyword argument to IPUMS extract classes to specify that the extract should include all individuals in households that contain a person with the specified :py:meth:`~ipumspy.api.BaseExtract.select_cases()` characteristics.
    * Added support for requesting hierarchical extracts: ``{"hierarchical": {}}`` is now an acceptable value for ``data_structure``
    * Added :py:class:`~ipumspy.api.extract.IpumsiExtract` class to support IPUMS International extract requests
    * Added :py:meth:`~ipumspy.api.IpumsApiClient.get_extract_history()` generator to allow for perusal of extract histories

  * Added :py:meth:`~ipumspy.api.IpumsApiClient.get_extract_by_id()` which creates a new (unsubmited) extract object from an IPUMS collection a previously submitted extract id number
  * Added support for reading hierarchical extract files in :py:meth:`~ipumspy.readers.read_hierarchical_microdata()`

* Bug Fixes

  * The ``subset`` argument for :py:meth:`~ipumspy.readers.read_microdata()` now functions correctly.

0.2.2-alpha.1
-------------
2023-03-06

* New minimum python version: Python 3.8
* Officially support Python 3.11

0.2.2-alpha
-----------
2023-01-31

* Officially support Python 3.10

0.2.1
-----
2022-05-23

* Update requirement to beautifulsoup4 instead of bs4

0.2.0
-----
2022-05-20

* New minimum python version: Python 3.7.1 
* Added support for IPUMS CPS extracts with :py:class:`~ipumspy.api.extract.CpsExtract`
* Added :py:class:`~ipumspy.utilities.CollectionInformation` class to access collection-level information about IPUMS data.
* Added ability to download Stata, SPSS, SAS, and R command files with data files :py:meth:`~ipumspy.api.IpumsApiClient.download_extract()`.
* Added :py:meth:`~ipumspy.api.extract.extract_to_dict()` and :py:meth:`~ipumspy.api.extract.extract_from_dict()` method to enable easy exporting of extract objects to dictionary objects and creation of extract objects from dictionaries.
* Added :py:meth:`~ipumspy.api.extract.define_extract_from_ddi()` method to re-create an IPUMS extract object from a DDI codebook.
* Added convenience method :py:meth:`~ipumspy.api.extract.save_extract_as_json()` to save IPUMS extract definition to json file.
* Added convenience method :py:meth:`~ipumspy.api.extract.define_extract_from_json()` to read an IPUMS extract definition from a json file.
* Added :py:meth:`~ipumspy.api.exceptions.IpumsExtractNotSubmitted` exception. This will be raised when attempting to retrieve an extract id or download link from a extract that has not been submitted to the IPUMS extract engine.
* Added :py:meth:`~ipumspy.ddi.Codebook.get_all_types()` method to access all types of ddi codebook variables in an easy way.
* Added parameter `string_pyarrow` to :py:meth:`~ipumspy.ddi.Codebook.get_all_types()` method. If this parameter is set to True and used in conjunction
  with parameter `type_format="pandas_type"` or `type_format="pandas_type_efficient"`, then the string column dtype (pandas.StringDtype()) is overriden with pandas.StringDtype(storage="pyarrow"). Useful for
  users who want to convert an IPUMS extract in csv format to parquet format.
  The dictionary returned by this method can then be used in the dtype argument of :py:meth:`~ipumspy.readers.read_microdata()` or :py:meth:`~ipumspy.readers.read_microdata_chunked()`.
* Added :py:meth:`~ipumspy.ddi.VariableDescription.pandas_type_efficient`. This type format is more efficient than `pandas_type`
  and is a sort of mix between `pandas_type` and `numpy_type`. Integer and float variables are coded as `numpy.float64`, string as `pandas.StringDtype()`.

0.1.0
-----
2021-11-30

* This is the initial version of ipumspy.
