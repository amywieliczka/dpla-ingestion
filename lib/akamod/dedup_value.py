from akara import logger
from akara import response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.selector import getprop, setprop, exists
from dplaingestion.utilities import load_json_body
import re

@simple_service('POST', 'http://purl.org/la/dp/dedup_value', 'dedup_value',
                'application/json')
@load_json_body(response)
def dedup_value(data, ctype, action="dedup_value", prop=None):
    '''
    Service that accepts a JSON document and enriches the prop field of that
    document by removing duplicate array elements
    '''

    if prop:
        for p in prop.split(","):
            if exists(data, p):
                v = getprop(data, p)
                if isinstance(v, list):
                    # Remove whitespace, periods, parens, brackets
                    clone = [_stripped(s) for s in v if _stripped(s)]
                    # Get index of unique values
                    index = list(set([clone.index(s)
                                      for s in list(set(clone))]))
                    setprop(data, p, [v[i] for i in index])

    return json.dumps(data)

def _stripped(thing):
    if isinstance(thing, basestring):
        return re.sub("[ \.\(\)\[\]\{\}]", "", thing).lower()
    else:
        return str(thing)
