.. ipumspy introduction

.. currentmodule:: ipumspy

What is IPUMS?
==============

IPUMS provides census and survey data from around the world integrated across time and space. 
IPUMS integration and documentation makes it easy to study change, conduct comparative research, merge information across data types, and analyze individuals within family and community contexts. 
Data and services available free of charge. More information on IPUMS data collections can be found at `ipums.org <https://ipums.org>`_.

What is ipumspy?
================

``ipumspy`` is a collection of python tools for working with data from `IPUMS <https://ipums.org>`_) and for accessing that data via API.

Only rectangular, microdata extracts are currently supported. We hope to add support for more complex data structures and spatial data in the future.

IPUMS USA is currently the only IPUMS microdata collection available via API. As other support for other IPUMS data collections will be added as they become available via API.
For more information about IPUMS account registration and API keys, see `here <https://developer.ipums.org/docs/get-started/>`_.

``ipumspy`` can also be used to analyze rectangular extracts made through the IPUMS website for collections unavailable via API.

