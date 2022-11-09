import hashlib
import sys
from amara.thirdparty import json
from amara.lib.iri import is_absolute
from akara.services import simple_service
from akara.util import copy_headers_to_dict
from akara import request, response
from dplaingestion.selector import getprop, setprop, exists
from utilities import load_json_body

COUCH_ID_BUILDER = lambda src, lname: "--".join((src,lname))
COUCH_REC_ID_BUILDER = lambda src, id_handle: COUCH_ID_BUILDER(src,id_handle.strip().replace(" ","__"))

def couch_record_id_builder(source_name, objid):
    lname = objid.strip().replace(" ", "__")
    f"{source_name}--{lname}"

@simple_service('POST', 'http://purl.org/la/dp/select-oac-id', 'select-oac-id',
                'application/json')
@load_json_body(response)
def selectid(data, ctype):
    '''   
    Service that accepts a JSON document and adds or sets the "id" property to
    the value of the property named by the "prop" paramater
    '''   

    request_headers = copy_headers_to_dict(request.environ)
    source_name = request_headers.get('Source')

    objid = None
    id_values = getprop(data, 'identifier')
    if isinstance(id_values,basestring):
        objid = id_values
        lname = objid.strip().replace(" ", "__")
        data[u'_id'] = f"{source_name}--{lname}"
        data[u'id'] = hashlib.md5(data[u'_id']).hexdigest()
        data[u'isShownAt'] = objid
        data[u'isShownBy'] = objid + '/thumbnail'
        return json.dumps(data)

    if not isinstance(id_values, list):
        id_values = [id_values]
    for id_value in id_values:
        if id_value['text'].startswith('http://ark.cdlib.org/ark:'):
            if is_absolute(id_value['text']):
                objid = id_value['text']
        if not objid:
            objid = id_value[0]

    if not objid:
        response.code = 500
        response.add_header('content-type', 'text/plain')
        return "No id property was found"

    data[u'_id'] = COUCH_REC_ID_BUILDER(source_name, objid)
    data[u'id']  = hashlib.md5(data[u'_id']).hexdigest()
    data[u'isShownAt'] = objid
    data[u'isShownBy'] = objid + '/thumbnail'

    return json.dumps(data)
