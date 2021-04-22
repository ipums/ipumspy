import os
import pytest

from ipumspy import apiutils


@pytest.fixture(params=[os.getenv('MY_KEY')])
def api_util(request):
    return apiutils.ApiUtilities(request.param)

def test_build_extract(api_util):
    '''
    Confirm that text extract formatted correctly
    '''
    #api_util = apiutils.ApiUtilities(api_key)
    extract = api_util.extract_request
    extract.build('cps',
                 ['cps1976_01s', 'cps1976_02b'],
                 ['YEAR', 'MISH', 'AGE',
                 'RACE', 'UH_SEX_B1'])
    extract_def = extract.extract_definition
    assert extract_def == {
                            'data_structure': { 
                                'rectangular': {
                                    'on': 'P'
                                }
                            },
                            'samples': {
                            'cps1976_01s': {},
                            'cps1976_02b': {}
                            },
                            'variables':{
                            'YEAR': {},
                            'MISH': {},
                            'AGE': {},
                            'RACE': {},
                            'UH_SEX_B1': {}
                            },
                            'description': 'My IPUMS extract',
                            'data_format': 'fixed_width',
                        }
    assert extract.product == 'cps'
    
def test_submit_extract(api_util):
    api_util.extract_request.build('cps',
                                   ['cps1976_01s', 'cps1976_02b'],
                                   ['YEAR', 'MISH', 'AGE',
                                    'RACE', 'UH_SEX_B1'])
    extract = api_util.extract_request.submit()
    assert extract.status_code == 200

def test_retrieve_previous_extracts(api_util):
    previous = api_util.extract_history.retrieve_previous_extracts('cps')
    assert len(previous) == 10

