import requests
import requests.exceptions

from pathlib import Path

class IpumsApiClient(object):
    def __init__(self, api_key, api_version='v1'):
        self.api_key = api_key
        self.api_version = api_version
        self.base_url = 'https://demo.api.ipums.org/extracts'

    def build_extract(self, product, samples, variables, 
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

        return request_body

    def submit_extract(self, product, request_body):
        extract = ApiRequestWrapper.api_call('post', 
                                            self.base_url, 
                                            params = {'product': product, 
                                                    'version': self.api_version},
                                            json=request_body, 
                                            headers={'Authorization': self.api_key})
        if extract is not None:
            extract_number = extract.json()['number']
        else:
            extract_number = None
        return (extract, extract_number)

    def extract_status(self, product, extract_number):
        new_url = f'{self.base_url}/{extract_number}'
        extract_status = ApiRequestWrapper.api_call('get', 
                                                    new_url, 
                                                    params = {'product': product, 
                                                            'version': self.api_version},
                                                    headers={'Authorization': self.api_key})
        return extract_status.json()['status']

    def download_extract(self, product, extract_number, download_dir=None):
        # if download_dir specified check if it exists
        if download_dir is None:
            download_dir = str(Path.cwd())
        else:
            if not Path(download_dir).exists():
                raise IOError(f'{download_dir} does not exist.')
        # check to see if extract complete
        if self.extract_status(product, extract_number) != "completed":
            raise RuntimeError(f'Your IPUMS extract number {extract_number} is not finished yet!')
        else:
            print('..shouldnt be here')
            new_url = f'{self.base_url}/{extract_number}'
            extract = ApiRequestWrapper.api_call('get', 
                                                new_url, 
                                                params = {'product': product, 
                                                            'version': self.api_version},
                                                headers={'Authorization': self.api_key})
            download_links = extract.json()['download_links']
            data_url = download_links['data']['url']
            ddi_url = download_links['ddi_codebook']['url']
            files = [data_url, ddi_url]
            for f in files:
                file_name = f.split('/')[-1]
                download_path = str(Path(download_dir, file_name))
                print(download_path)
                with requests.get(f, stream=True, headers={'Authorization': self.api_key}) as r:
                    r.raise_for_status()
                    with open(download_path, 'wb') as fh:
                        for chunk in r.iter_content(chunk_size=1024):
                            fh.write(chunk)

    def retrieve_previous_extracts(self, product, N='10'):
        previous_extracts = ApiRequestWrapper.api_call('get', 
                                                        self.base_url, 
                                                        params = {'product': product, 
                                                                  'limit': N,
                                                                  'version': self.api_version},
                                                        headers={'Authorization': self.api_key})
        return previous_extracts.json()

    def wait_for_extract(self):
        # wrap check_status
        pass


class ApiRequestWrapper():
    @staticmethod
    def api_call(*args, **kwargs):
        try:
            response = requests.request(*args, **kwargs)  
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            try:
                error_details = '\n'.join(response.json()['detail']['base'])
                print(error_details)
            except KeyError:
                pass
        except Exception as err:
            print(f'other error occured: {err}')



    
        