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
* Added :py:meth:`~ipumspy.api.exceptions.IpumsExtractNotSubmitted` exception. This will be raised when attempting to retrieve an extract id or download link from a extract that has not been submitted to the IPUMS extract engine.
* Added ability to download Stata, SPSS, SAS, and R command files with data files :py:meth:`~ipumspy.api.IpumsApiClient.download_extract()`.
* Added support for IPUMS CPS extracts with :py:class:`~ipumspy.api.extract.CpsExtract`
* New minimum python version: Python 3.7.1 

0.1.0
-----
2021-11-30

* This is the initial version of ipumspy.