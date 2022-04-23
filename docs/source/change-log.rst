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
* New minimum python version: Python 3.7.1 
* Added :py:meth:`~ipumspy.ddi.Codebook.get_all_types()` method to access all types of ddi codebook variables in an easy way.
* Added parameter `string_pyarrow` to :py:meth:`~ipumspy.ddi.Codebook.get_all_types()` method. If this parameter is set to True and used in conjunction
  with parameter `type_format="pandas_type"` or `type_format`="pandas_type_efficient"`, then the string column dtype (pandas.StringDtype()) is overriden with pandas.StringDtype(storage="pyarrow"). Useful for
  users who want to convert an IPUMS extract in csv format to parquet format.
  The dictionary returned by this method can then be used in the dtype argument of :py:meth:`~ipumspy.readers.read_microdata()` or :py:meth:`~ipumspy.readers.read_microdata_chunked()`.
* Added :py:meth:`~ipumspy.ddi.VariableDescription.pandas_type_efficient`. This type format is more efficient than `pandas_type`
  and is a sort of mix between `pandas_type` and `numpy_type`. Integer and float variables are coded as `numpy.float64`, string as `pandas.StringDtype()`.


0.1.0
-----
2021-11-30

* This is the initial version of ipumspy.
