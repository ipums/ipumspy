import requests


class ApiUtilities(object):
    def __init__(self, api_key, api_version='v1'):
        self.api_key = api_key
        self.api_version = api_version
        # maybe want to have these in an external config file somewhere?
        self.base_url = 'https://demo.api.ipums.org/extracts'

    def retrieve_previous_extracts(self, product, N='10'):
        """
        Returns a list of N previously submitted extract definitions.

        Args:
            N: Number of previous extracts to retrieve. Default is 10.

        Returns:
            A list of the user's N previously submitted extract definitions.
        """

        previous_extracts = requests.get(self.base_url, 
                                         params={'product': product, 
                                                 'limit': N, 
                                                 'version': self.api_version}, 
                                         headers={'Authorization': self.api_key})
        return previous_extracts

    def retrieve_extract_definition(self, product, extract_number):
        ## modify base url to be for specific extract number
        extract_url = f'{self.base_url}/{extract_number}'
        extract = requests.get(extract_url,
                               params={'product': product,
                                       'version': self.api_version},
                               headers={'Authorization': self.api_key})
        # request error handling?
        extract_definition = extract.json()
        extract_definition.pop('download_links')
        extract_definition.pop('number')
        extract_definition.pop('status')
        return extract_definition


class ExtractRequest(ApiUtilities):
    def __init__(self, product, samples, variables, api_key, 
                 data_format='fixed_width', description='My IPUMS extract',
                 api_version='v1'):
        # the way the api_version arg is handled here seems less than ideal
        super(ExtractRequest, self).__init__(api_key, api_version)
        self.product = product
        self.samples = samples
        self.variables = variables
        self.data_format = data_format
        self.description = description
        self.number = None
        self.status = 'built'
        
        self.extract_definition = self.build()


    def build(self):
        request_body = {
            'data_structure':{
                'rectangular':{
                    'on': 'P'
                }
            },
            'samples': {},
            'variables': {}
        }

        # add extract description
        request_body['description'] = self.description
        # add data format
        request_body['data_format'] = self.data_format
        # add samples
        for sample in self.samples:
            request_body['samples'][sample] = {}

        for variable in self.variables:
            request_body['variables'][variable.upper()] = {}

        return request_body
    
    def submit(self):
        extract = requests.post(self.base_url, 
                                params = {'product': self.product, 
                                          'version': self.api_version},
                                json=self.extract_definition, 
                                headers={'Authorization': self.api_key})
        # request error handling?
        self.number = extract.json()['number']
        self.status = extract.json()['status']
        return extract

    def check_status(self):
        pass

    def download(self):
        pass

###########
# TESTING #
###########
import os
my_api_key = os.getenv("MY_KEY")
extract_request = ExtractRequest('usa', ['us2012b'], ['YEAR'], my_api_key)
#print(extract_request.api_key)

# extract_def = extract_request.build()
# extract_def = extract_request.extract_definition
# print(extract_def)
# extract_req = extract_request.submit()
# print(extract_req)
# print(extract_request.number)
# print(extract_request.status)

apiutil = ApiUtilities(my_api_key, api_version='v1')
extract_list = apiutil.retrieve_previous_extracts('usa', N='2')
#print(extract_list.json())
print(len(extract_list.json()))
resub_ext = extract_list.json()[0]
print(resub_ext)
resub = apiutil.retrieve_extract_definition('usa', '8')
print(resub)