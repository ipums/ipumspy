# IPUMS-py

A collection of tools for working with data from [IPUMS](https://ipums.org).

## Requirements

This package requires that you have at least Python 3.6 installed. If so, then you should
simply be able to pip install it.

```bash
pip install ipumspy
```

## Microdata API integration usage

An example of how to create, submit, and download an IPUMS extract via `ipumspy`.

First get an IPUMS API key [instructions and link to do that eventually].

Build an extract by supplying a data collection, a list of samples, and a list of variables.
For a list of sample ids by collection, see [link here eventually].

```python
from ipumspy import IpumsApi

ipums = IpumsApi(your_api_key)

# Submit an API extract request
extract_number = ipums.cps.submit_extract(
    ["cps1976_01s"],
    ["YEAR", "AGE"],
)
```

This returns the number of the extract you just submitted. You will need the extract number to check the status of your extract and to download it once it is completed.

Wait for your extract to complete. The extract in this example is quite small and will
take less than a minute to complete.

```python
import itertools as its
import time

for i in its.count():
     print("...waiting....")
     time.sleep(i * 15)

     #check extract status
     extract_status = ipums.cps.extract_status(extract_number)
     print(f"extract {extract_number} is {extract_status}")
     if extract_status == "completed":
         break
```

Once the extract is complete, specify the IPUMS data product/collection and number of your extract to download.

```python
ipums.cps.download_extract(extract_number)
```
