.. ipumspy documentation for the command line interface

.. currentmodule:: ipumspy

.. _cli:

Command Line Interface
======================

``ipumspy`` allows you to interact with the IPUMS API via the command line. If you
have :doc:`installed <getting_started>` with ``pip``, then you should have an ``ipums``
command available on the command line.

You can explore what commands are available by running the ``--help`` option:

.. code:: bash

    ipums --help

In particular, suppose that you have specified an extract in an ``ipums.yml`` file
as described in the :doc:`getting started guide <getting_started>`.

.. code:: yaml

    description: Simple IPUMS extract
    collection: usa
    api_version: 2
    samples:
      - us2012b
    variables:
      - AGE
      - SEX

Then you can submit, wait for, and download the extract in a single line:

.. code:: bash

    ipums submit-and-download -k <IPUMS_API_KEY> ipums.yml

Much of the rest of the functionality of the library is also available on the command
line, as this document describes.

Environment Variables
*********************

For security, it is recommended that you not pass your API key directly on the
command line. The ``ipums`` command will look for your API key in the ``IPUMS_API_KEY``
environment variable.

Specifying Multiple Extracts
****************************

You may create mutliple files specifying extracts. For instance, in addition to the
``ipums.yml`` described above, you might also have a file called ``ipums_with_race.yml``
which contains the following:

.. code:: yaml

    description: Another extract
    collection: usa
    api_version: 2
    samples:
      - us2012b
    variables:
      - AGE
      - SEX
      - RACE

Then the following command would submit and download this extract:

.. code:: bash

    ipums submit-and-download -k <IPUMS_API_KEY> ipums_with_race.yml

Alternatively, the ``submit-and-download`` command also allows you to specify *multiple*
extracts simultaneously. To do so, specify the ``ipums_multiple.yml`` file as follows:

.. code:: yaml

    extracts:
    - description: Simple IPUMS extract
      collection: usa
      api_version: 2
      samples:
        - us2012b
      variables:
        - AGE
        - SEX
    - description: Another extract
      collection: usa
      api_version: 2
      samples:
        - us2012b
      variables:
        - AGE
        - SEX
        - RACE

Note that this specifies a dictionary with one key (``extracts``) whose value is a list
of extract specifications. Then you can submit and download these extracts with the
command:

.. code:: bash

    ipums submit-and-download -k <IPUMS_API_KEY> ipums_multiple.yml

Step-by-Step
************

The introduction provided an all-in-one command ``submit-and-download`` that submits,
waits for, and downloads and IPUMS extract. But sometimes you may wish to break up the
steps (e.g., you want to redownload an extract that has already been prepared). This
functionlaity is available via the ``submit``, ``check``, and ``download`` commands:

.. code:: bash

    ipums submit -k <IPUMS_API_KEY> ipums.yml
    # Your extract for collection usa has been successfully submitted with number 10

    ipums check -k <IPUMS_API_KEY> 10
    # Extract 10 in collection usa has status started

    # "started" means that your extract has been queued
    # You should wait until the status is "completed"
    ipums check -k <IPUMS_API_KEY> 10
    # Extract 10 in collection usa has status completed

    ipums download -k <IPUMS_API_KEY> 10

Extra options
*************

These commands provide several extra options, which may be found by running any command
with the ``--help`` option, for example:

.. code:: bash

    ipums submit --help

Here we enumerate a few for reference:

    * ``-k``: For commands that require your API key, this is used to specify the API key. In every case, you can also specify your key via the ``IPUMS_API_KEY`` environment variable.
    * ``-o``: For commands that download an extract, this may be used to specify which directory the extract will be downloaded to. The default is always the current directory.

Parquet
*******

For repeated use of a data set, we encourage you to store the data set as `parquet <https://parquet.apache.org/documentation/latest/>`_. This will greatly facilitate loading the data into memory or working with tools like `dask <https://dask.org>`_. We've provided a convenient command line tool for this conversion.

Suppose you've downloaded an extract into ``usa_00006.dat`` whose DDI is specified in ``usa_00006.xml``. Then you can convert this to a parquet file called ``usa_00006.parquet`` as follows:

.. code:: bash

    ipums convert usa_00006.xml usa_00006.dat usa_00006.parquet

Once you have the parquet file in hand, you can load it the same way you would any
other IPUMS file:

.. code:: python

    import ipumspy

    ddi = ipumspy.read_ipums_ddi(ddi_file)
    ipums_df = ipumspy.read_microdata(ddi, "usa_00006.parquet")
