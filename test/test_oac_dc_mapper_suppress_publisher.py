import os.path as path
from unittest import TestCase
from server_support import server, H
from amara.thirdparty import json

DIR_FIXTURES = path.join(path.abspath(path.split(__file__)[0]), 'fixtures')

#http://stackoverflow.com/questions/18084476/is-there-a-way-to-use-python-unit-test-assertions-outside-of-a-testcase
TC = TestCase('__init__')

def _get_server_response(body):
    url = server() + "dpla_mapper?mapper_type=oac_dc_suppress_publisher"
    return H.request(url, "POST", body=body)

def test_suppress_description_2():
    '''Test that the publisher from OAC is not pulled to sourceResource'''
    fixture = path.join(DIR_FIXTURES, 'oac-xml.json')
    with open(fixture) as f:
        INPUT = f.read()
    resp, content = _get_server_response(INPUT)
    TC.assertEqual(resp.status, 200)
    content_obj = json.loads(content)
    srcRes = content_obj['sourceResource']
    TC.assertNotIn('publisher', srcRes)
