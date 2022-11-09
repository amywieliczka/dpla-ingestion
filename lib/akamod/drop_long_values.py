# pass in a Couchdb doc, get back one with de-duplicated sourceResource values
from amara.thirdparty import json
from akara.services import simple_service
from akara import response
from dplaingestion.utilities import load_json_body

@simple_service('POST', 'http://purl.org/org/cdlib/ucldc/drop-long-values',
                'drop-long-values', 'application/json')
@load_json_body(response)
def drop_long_values(data, ctype, field=None, max_length=150):
    ''' Look for long values in the sourceResource field specified.
    If value is longer than max_length, delete
    '''
    fieldvalues = data['sourceResource'].get(field)
    if isinstance(fieldvalues, list):
        new_list = []
        for item in fieldvalues:
            if len(item) <= int(max_length):
                new_list.append(item)
        data['sourceResource'][field] = new_list
    else:  # scalar
        if len(fieldvalues) > int(max_length):
            del data['sourceResource'][field]

    return json.dumps(data)
