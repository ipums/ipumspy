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

```
ipums = IpumsApiClient(your_api_key)

extract_definition = ipums.build_extract('cps', 
                                        ['cps1976_01s'],
                                        ['YEAR', 'AGE'])
```
This returns a json formatted for submission to the IPUMS microdata extract api.

Submit the extract.

```
extract, extract_number = ipums.submit_extract('cps', 
                                               extract_definition)
```
This returns the API response and the number of the extract you just submitted. You will need the extract number to check the status of your extract and to download it once it is completed.

Wait for your extract to complete. The extract in this example is quite small and will
take less than a minute to complete.

```
for i in range(1,5):
     print('...waiting....')
     time.sleep(i*15)
     #check extract status
     extract_status = ipums.extract_status('cps', extract_number)
     print(f'extract {extract_number} is {extract_status}')
     if extract_status == "completed":
         break
```

Once the extract is complete, specify the IPUMS data product/collection and number of your extract to download.

```
ipums.download_extract('cps', extract_number)
```
