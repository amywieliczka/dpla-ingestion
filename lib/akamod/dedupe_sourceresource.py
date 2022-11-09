# pass in a Couchdb doc, get back one with de-duplicated sourceResource values
from amara.thirdparty import json
from amara.lib.iri import is_absolute
from akara.services import simple_service
from akara.util import copy_headers_to_dict
from akara import request, response
from dplaingestion.selector import getprop, setprop, exists
from dplaingestion.utilities import load_json_body

@simple_service('POST', 'http://purl.org/org/cdlib/ucldc/dedupe-sourceresource',
                'dedupe-sourceresource',
                'application/json')
@load_json_body(response)
def dedupe_srcres(data, ctype):
    '''Remove blank values from the sourceResource'''
    for key, value in data['sourceResource'].items():
        if not value:
            del data['sourceResource'][key]
        if value == [u'none'] or value == [u'[none]']:
            del data['sourceResource'][key]
    
    for key, value in data['sourceResource'].items():
        if isinstance(value, list):
            # can't use set() because of dict values (non-hashable)
            new_list = []
            for item in value:
                if item not in new_list:
                    new_list.append(item)
            data['sourceResource'][key] = new_list
    return json.dumps(data)

