[![Build Tests](https://github.com/ipums/ipumspy/actions/workflows/main.yml/badge.svg)](https://github.com/ipums/ipumspy/actions/workflows/main.yml)

# IPUMS-py

A collection of tools for working with data from [IPUMS](https://ipums.org).

## Requirements

This package requires that you have at least Python 3.6 installed. If so, then you should
simply be able to pip install it.

```bash
pip install ipumspy
```

## Read an IPUMS extract

The following code parses an IPUMS extract DDI xml codebook and data file and returns a pandas data frame.
Both fixed-width and csv files are supported.

```python
from ipumspy import readers, ddi

ddi_codebook = readers.read_ipums_ddi([ddi xml file path])
ipums_df = readers.read_microdata(ddi_codebook, [data file path])
```

## IPUMS variable information

The `VariableDescription` objects built from the ddi codebook provide easy access to variable metadata.
These can ge returned using the `get_variable_info()` method.

```python
from ipumspy import readers, ddi, utilities

# read ddi and data
ddi_codebook = readers.read_ipums_ddi([ddi xml file path])
ipums_df = readers.read_microdata(ddi_codebook, [data file path])

# get VariableDescription for SEX
sex_info = ddi_codebook.get_variable_info('SEX')

# see codes and labels for SEX
print(sex_info.codes)

# see variable description for SEX
print(sex_info.description)
```
The above code results in the following:

```
# codes and labels
{'Male': 1, 'Female': 2}

# description
'SEX reports whether the person was male or female.'
```

## More on value labels
Users can filter on categorical variables using labels instead of numerical values
For example, the following code retains only the female respondents in `ipums_df`.

```python
# retrieve the VaribleDescription for the variable SEX
sex_info = ddi_codebook.get_variable_info('SEX')
women = ipums_df[ipums_df['SEX'] == sex_info.codes['Female']]
```

It is possible to filter on both categorical variables using labels and on numerical values.
The following retains only women over the age of 16 in `ipums_df`

```python
adult_women = ipums_df[(ipums_df['SEX'] == sex_info.codes['Female']) & (ipums_df['AGE'] > 16)]
```

## Microdata API integration usage

An example of how to create, submit, and download an IPUMS extract via `ipumspy`.

First get an IPUMS API key [instructions and link to do that eventually].

Build an extract by supplying a data collection, a list of samples, and a list of variables.
For a list of sample ids by collection, see [link here eventually].

```python
from ipumspy import IpumsApiClient, UsaExtract

ipums = IpumsApiClient(your_api_key)

# Submit an API extract request
extract = UsaExtract(
    ["us2012b"],
    ["AGE", "SEX"],
)
ipums.submit_extract(extract)
print(f"Extract submitted with id {extract.extract_id}")
```

Wait for your extract to complete. The extract in this example is quite small and will
take less than a minute to complete.

```python
import itertools as its
import time

for i in its.count():
     print("...waiting....")
     time.sleep(i * 15)

     #check extract status
     extract_status = ipums.extract_status(extract)
     print(f"extract {extract.extract_id} is {extract_status}")
     if extract_status == "completed":
         break
```

Once the extract is complete, specify the IPUMS data product/collection and number of your extract to download.

```python
ipums.download_extract(extract)
```

If for any reason you lose track of the `extract` object, you may check the status
and download the extract using only the name of the `collection` and the `extract_id`.

```python
for i in its.count():
    print("...waiting....")
    time.sleep(i * 15)

    # check extract status
    extract_status = ipums.extract_status(extract=extract_id, collection="usa")
     print(f"extract {extract_id} is {extract_status}")
     if extract_status == "completed":
         break

ipums.download_extract(extract=extract_id, collection="usa")
```
