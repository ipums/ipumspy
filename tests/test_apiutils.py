import os
import pytest

from ipumspy import apiutils


@pytest.fixture(params=[os.getenv('MY_KEY')])
def api_util(request):
    return apiutils.IpumsApiClient(request.param)

def test_build_extract(api_util):
    '''
    Confirm that test extract formatted correctly
    '''

    extract = api_util.build_extract('cps',
                                    ['cps1976_01s', 'cps1976_02b'],
                                    ['YEAR', 'MISH', 'AGE',
                                    'RACE', 'UH_SEX_B1'])
    assert extract == {
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
    
def test_submit_extract(api_util):
    '''
    Confirm that test extract submits properly
    '''
    extract_def = api_util.build_extract('cps',
                                        ['cps1976_01s', 'cps1976_02b'],
                                        ['YEAR', 'MISH', 'AGE',
                                         'RACE', 'UH_SEX_B1'])
    extract, number = api_util.submit_extract('cps', extract_def)
    assert extract.status_code == 200

def test_retrieve_previous_extracts(api_util):
    previous = api_util.retrieve_previous_extracts('cps')
    assert len(previous) == 10

