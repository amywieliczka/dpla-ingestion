"""
 Akara module that provides cleaning endpoints:
 - filter_empty_values: cleans empty leaves of given json;
 - filter_fields: cleans elements of json with given top-level keys if corresponding value is empty;

 to test locally, save TEST_EXAMPLE to local file (i.e. artstor_doc.js) and then run:

 curl -X POST -d @test/artstor_doc.js -H "Content-Type: application/json" http://localhost:8879/filter_empty_values
"""

__author__ = 'Alexey R.'

from akara import logger
from akara import response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.utilities import load_json_body

def filter_fields(d, check_keys=tuple()):
    for k, v in d.items():
        if check_keys and k not in check_keys:
            continue
        elif isinstance(v, dict) and v:
            d[k] = filter_fields(v)
        elif isinstance(v, list) and v:
            d[k] = [filter_fields(e) if isinstance(e, dict) else e for e in v]
        elif not v:
            del d[k]
    return d

@simple_service('POST', 'http://purl.org/la/dp/filter_fields', 'filter_fields',
                'application/json')
@load_json_body(response)
def filter_fields_endpoint(data, ctype, keys):
    filter_fields(data, ["sourceResource"])
    return json.dumps(data)
