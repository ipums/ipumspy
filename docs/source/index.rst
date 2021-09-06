.. ipumspy master documentation file

IPUMS API Wrappers for Python
=============================

``ipumspy`` provides an easy-to-use Python wrapper for IPUMS API endpoints.


.. _installation:


Install
-------

Install with `pip`:

.. code:: bash

    pip install ipumspy

Or conda:

.. code:: bash

    conda install -c conda-forge ipumspy


Quick Start
-----------

.. code:: python

    import itertools as its
    import time
    from pathlib import Path

    from ipumspy import IpumsApiClient, UsaExtract

    IPUMS_API_KEY = your_api_key
    DOWNLOAD_DIR = Path(your_download_dir)

    ipums = IpumsApiClient(IPUMS_API_KEY)

    # Submit an API extract request
    extract = UsaExtract(
        ["us2012b"],
        ["AGE", "SEX"],
    )
    ipums.submit_extract(extract)
    print(f"Extract submitted with id {extract.extract_id}")

    # Wait for the extract to finish
    for i in its.count():
        print("...waiting....")
        time.sleep(i * 15)

        # check extract status
        extract_status = ipums.extract_status(extract)
        print(f"extract {extract.extract_id} is {extract_status}")
        if extract_status == "completed":
            break

    # Download the extract
    ipums.download_extract(extract, download_dir=DOWNLOAD_DIR)

    # Get the DDI
    ddi_file = list(DOWLOAD_DIR.glob("*.xml"))[0]
    ddi = ipumspy.read_ipums_ddi(ddi_file)

    # Get the data
    ipums_df = ipumspy.read_microdata(ddi, DOWNLOAD_DIR / ddi.file_description.filename)


Contributing
------------

All contributions, bug reports, bug fixes, documentation improvements,
enhancements and ideas are welcome.

A detailed overview on how to contribute can be found in the
`contributing
guide <https://github.com/ipums/ipumspy/blob/master/CONTRIBUTING.md>`__
on GitHub.

Issues
------

Submit issues, feature requests or bugfixes on
`github <https://github.com/ipumspy/ipums/issues>`__.

.. toctree::
    :maxdepth: 6
    :caption: Introduction
    :hidden:

    self

.. toctree::
    :maxdepth: 6
    :caption: User Guide
    :hidden:

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
