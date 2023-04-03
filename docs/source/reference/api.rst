.. _api-interface:

REST API Interface
==================

These objects are used to interact with the IPUMS REST API from Python.

Core API Interface
------------------

.. autosummary::
   :toctree: generated
   :template: class.rst
   :nosignatures:

   ipumspy.api.IpumsApiClient

Extract Wrappers
----------------

Different IPUMS collections may have *slightly* different query parameters.
Thus, to pull from a particular collection, you will need to use a particular
extract class.

.. autosummary::
   :toctree: generated
   :template: class.rst
   :nosignatures:

   ipumspy.api.BaseExtract
   ipumspy.api.OtherExtract
   ipumspy.api.UsaExtract
   ipumspy.api.CpsExtract
   ipumspy.api.IpumsiExtract

Importing or Exporting Extract Definitions
------------------------------------------
There are two convenience methods to transform ipumspy extract objects to dictionary 
objects and from dictonary objects to ipumspy extract objects.

.. autosummary::
   :toctree: generated
   :template: class.rst
   :nosignatures:

   ipumspy.api.extract_from_dict
   ipumspy.api.extract_to_dict
   ipumspy.api.extract.save_extract_as_json
   ipumspy.api.extract.define_extract_from_json

Exceptions
----------

Several different exceptions may be raised when interacting with the IPUMS API.

.. autosummary::
   :toctree: generated
   :template: class.rst
   :nosignatures:

   ipumspy.api.exceptions.IpumsApiException
   ipumspy.api.exceptions.TransientIpumsApiException
   ipumspy.api.exceptions.IpumsExtractNotReady
   ipumspy.api.exceptions.IpumsTimeoutException
   ipumspy.api.exceptions.IpumsAPIAuthenticationError
   ipumspy.api.exceptions.BadIpumsApiRequest
   ipumspy.api.exceptions.IpumsExtractNotSubmitted