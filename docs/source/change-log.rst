:orphan: Supress Sphinx warning about this file not being in any toctree

.. ipumspy version history

Change Log
==========

All noteable changes to this project are documented in this file.
This project adheres to `Semantic Versioning`_.

.. _Semantic Versioning: http://semver.org/


0.*.*
-----
year-month-day

* Added :py:meth:`~ipumspy.api.extract.extract_to_dict()` method to enable easy exporting of extract objects to dictionary objects for eventual writing to .json for ease of extract sharing.
* Added :py:meth:`~ipumspy.api.exceptions.IpumsExtractNotSubmitted` exception
* Added ability to download Stata, SPSS, SAS, and R command files with data files :py:meth:`~ipumspy.api.IpumsApiClient.download_extract()`.


0.1.0
-----
2021-11-30

* This is the initial version of ipumspy.


0.1.1-alpha
----
2022-04-14

* Added :py:meth:`~ipumspy.ddi.Codebook.get_all_types()` method to access all types of ddi codebook variables in an easy way.

2022-04-20

* Added parameter `string_pyarrow` to :py:meth:`~ipumspy.ddi.Codebook.get_all_types()` method. If this parameter is set to True is used in conjunction
  with parameter `type_format`="pandas_type", then the string column dtype (pd.StringDtype()) is overriden with pd.StringDtype(storage="pyarrow"). Useful for
  users who want to convert an IPUMS extract in csv format to parquet format.
