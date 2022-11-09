from amara.thirdparty import json
from akara.services import simple_service
from akara import request, response
#from akara import logger
from dplaingestion.selector import getprop, setprop, exists
from lib.utilities import load_json_body

@simple_service('POST',
    'http://purl.org/org/cdlib/ucldc/set-ucldc-dataprovider',
                'set-ucldc-dataprovider',
                'application/json')
@load_json_body(response)
def set_ucldc_dataprovider(data, ctype):
    '''For ucldc, we always have a originalRecord/collection entry.
    This has a repository object which may or may not have a list of 
    campuses.
    Concatenate the repo & campus if exisiting, separated by a ,
    for dataProvider value
    '''    
    collection = getprop(data,'originalRecord/collection')[0]
    repo = collection['repository'][0]
    campus = None
    if len(repo['campus']):
        campus = repo['campus'][0]
    dataProvider = repo['name']
    if campus:
        dataProvider = ', '.join((campus['name'], repo['name']))
    setprop(data, 'dataProvider', dataProvider)
    data['provider'] = {}
    setprop(data, 'provider/name', dataProvider)
    setprop(data, 'provider/@id', collection['@id'])
    data['sourceResource']['stateLocatedIn'] = [{'name':'California'}]
    return json.dumps(data)
