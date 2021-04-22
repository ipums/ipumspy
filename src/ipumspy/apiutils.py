import requests
import requests.exceptions

class ApiUtilities(object):
    def __init__(self, api_key, api_version='v1'):
        self.api_key = api_key
        self.api_version = api_version
        # maybe want to have these in an external config file somewhere?
        self.base_url = 'https://demo.api.ipums.org/extracts'
        self.extract_request = ExtractRequest(self.api_key, 
                                              self.api_version, 
                                              self.base_url)
        self.extract_history = ExtractHistory(self.api_key,
                                              self.api_version,
                                              self.base_url)

class ApiRequestWrapper():
    @staticmethod
    def api_call(*args, **kwargs):
        try:
            response = requests.request(*args, **kwargs)  
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as http_err:
            # this isn't actually giving us the 'details' from the error json returned by the api for 400 errors
            print(f'HTTP error occurred: {http_err}')
            error_details = '\n'.join(response.json()['detail']['base'])
            print(error_details)
        except Exception as err:
            print(f'other error occured: {err}')


class ExtractRequest():
    def __init__(self, api_key, api_version, base_url):
        self.api_key = api_key
        self.api_version = api_version
        self.base_url = base_url
        

    def build(self, product, samples, variables, 
              description='My IPUMS extract', data_format='fixed_width'):
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
        request_body['description'] = description
        # add data format
        request_body['data_format'] = data_format
        # add samples
        for sample in samples:
            request_body['samples'][sample] = {}

        for variable in variables:
            request_body['variables'][variable.upper()] = {}

        #return request_body
        self.extract_definition = request_body
        self.product = product

    
    def submit(self):
        extract = ApiRequestWrapper.api_call('post', 
                                            self.base_url, 
                                            params = {'product': self.product, 
                                                      'version': self.api_version},
                                            json=self.extract_definition, 
                                            headers={'Authorization': self.api_key})
        self.extract_number = extract.json()['number']
        self.extract_status = extract.json()['status']
        return extract


    def check_status(self):
        new_url = f'{self.base_url}/{self.extract_number}'
        extract_status = ApiRequestWrapper.api_call('get', 
                                                    new_url, 
                                                    params = {'product': self.product, 
                                                              'version': self.api_version},
                                                    headers={'Authorization': self.api_key})
        self.extract_status = extract_status.json()['status']


    def wait_for_extract():
        # wrap check_status
        pass


    def download():
        pass


class ExtractHistory():
    def __init__(self, api_key, api_version, base_url):
        self.api_key = api_key
        self.api_version = api_version
        self.base_url = base_url

    
    def retrieve_previous_extracts(self, product, N='10'):
        previous_extracts = ApiRequestWrapper.api_call('get', 
                                                        self.base_url, 
                                                        params = {'product': product, 
                                                                  'limit': N,
                                                                  'version': self.api_version},
                                                        headers={'Authorization': self.api_key})
        return previous_extracts.json()


    def retrieve_extract(self, product, extract_number):
        ## modify base url to be for specific extract number
        extract_url = f'{self.base_url}/{extract_number}'
        extract = ApiRequestWrapper.api_call('get', 
                                             extract_url, 
                                             params = {'product': product, 
                                                       'version': self.api_version},
                                             headers={'Authorization': self.api_key})
        # request error handling?
        return extract


