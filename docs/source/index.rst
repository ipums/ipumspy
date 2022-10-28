.. ipumspy master documentation file

What is IPUMS?
--------------

IPUMS provides census and survey data from around the world integrated across time and space. IPUMS integration and documentation makes it easy to study change, conduct comparative research, merge information across data types, and analyze individuals within family and community contexts. Data and services available free of charge. More information on IPUMS data collections can be found at `ipums.org <https://ipums.org>`_.

What is ipumspy?
----------------

``ipumspy`` is a collection of python tools for working with data from `IPUMS <https://ipums.org>`_ and for accessing that data via API.

Only rectangular microdata extracts are currently supported. We hope to add support for more complex data structures and spatial data in the future.

IPUMS USA and IPUMS CPS are currently the only IPUMS microdata collection available via the IPUMS microdata extract API. Support for other IPUMS data collections will be added as they become available via API.
For more information about the IPUMS API program, IPUMS account registration, and API keys, se the `IPUMS developer portal <https://external-api-docs-microdata-documentation.dev.ipums.org/>`_.

``ipumspy`` can also be used to analyze rectangular extracts made through the IPUMS website for collections unavailable via API.


Releases
--------

This library's :doc:`change-log` details changes and fixes made with each release.

How to Cite
-----------

If you use ``ipumspy`` in the context of academic or industry research, please
cite IPUMS. For any given extract, the appropriate citation may be found in the
accompanying DDI at:

.. code:: python

    print(ddi.ipums_citation)

License and Credits
-------------------

``ipumspy`` is licensed under the `Mozilla Public License Version 2.0 <https://github.com/ipums/ipumspy/blob/master/LICENSE>`_.


Indices and tables
==================

* :ref:`genindex`

.. toctree::
   :maxdepth: 6
   :caption: User Guide
   :hidden:

   getting_started
   extracts
   variables
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