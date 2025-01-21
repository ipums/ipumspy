.. ipumspy master documentation file

What is IPUMS?
--------------

IPUMS provides census and survey data from around the world integrated across time and space. IPUMS integration and documentation makes 
it easy to study change, conduct comparative research, merge information across data types, and analyze individuals within family 
and community contexts. Data and services available free of charge. More information on IPUMS data collections can be 
found at `ipums.org <https://ipums.org>`_.

What is ipumspy?
----------------

ipumspy is a collection of python tools for working with data downloaded from `IPUMS <https://ipums.org>`_ and for accessing that 
data via the `IPUMS API <https://developer.ipums.org/>`_.

ipumspy can only be used to request data for IPUMS data collections supported by the IPUMS API. See the :ref:`collection support table` table 
for a list of currently supported collections. Support for other IPUMS data collections will be added as they become available via API.

For more information about the IPUMS API program, IPUMS account registration, and API keys, see 
the `IPUMS developer portal <https://developer.ipums.org/docs/apiprogram/>`_.

Even for collections not yet supported by the API, ipumspy can be used to read and analyze
data downloaded from the IPUMS website.

Releases
--------

This library's :doc:`change-log` details changes and fixes made with each release.

How to Cite
-----------

If you use ipumspy in the context of academic or industry research, please
cite IPUMS. For any given extract, the appropriate citation may be found in the
accompanying DDI at:

.. code:: python

    print(ddi.ipums_citation)

License and Credits
-------------------

ipumspy is licensed under the `Mozilla Public License Version 2.0 <https://github.com/ipums/ipumspy/blob/master/LICENSE>`_.


Indices and tables
==================

* :ref:`genindex`

.. toctree::
   :maxdepth: 6
   :caption: User Guide
   :hidden:

   getting_started
   ipums_api/index
   reading_data
   cli

.. toctree::
   :maxdepth: 6
   :caption: Reference
   :hidden:

   reference/index

.. toctree::
   :maxdepth: 6
   :caption: Community
   :hidden:

   CONTRIBUTING

.. toctree::
   :maxdepth: 6
   :caption: Project History
   :hidden:

   change-log