import numbers
from akara import response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.selector import getprop, setprop


def jsonfy_obj(data):
    '''Jsonfy a python dict object. For immediate sub items (not recursive yet
    if the data can be turned into a json object, do so.
    Unpacks string json objects buried in some blacklight/solr feeds.
    '''
    obj_jsonfied = {}
    if isinstance(data, numbers.Number) or isinstance(data, bool):
        return data
    if isinstance(data, str):
        try:
            x = json.loads(data)
        except (ValueError, TypeError) as e:
            x = data
        return x
    for key, value in list(data.items()):
        if isinstance(value, list):
            new_list = []
            for v in value:
                try:
                    x = jsonfy_obj(v)
                    new_list.append(x)
                except (ValueError, TypeError) as e:
                    new_list.append(v)
            obj_jsonfied[key] = new_list
        else:  # usually singlevalue string, not json
            try:
                x = json.loads(value)
                # catch numbers already typed as singlevalue strings
                if isinstance(x, int):
                    x = value
            except (ValueError, TypeError) as e:
                x = value
            obj_jsonfied[key] = x
    return obj_jsonfied


@simple_service("POST", "http://purl.org/la/dp/jsonfy-prop", "jsonfy-prop",
                "application/json")
@load_json_body(response)
def jsonfy_prop(data, ctype, prop=None):
    """ Some data is packed as strings that contain json. (UCSD)
    Take the data in the given property and turn any sub-values that can be
    read by json.loads into json object.
    """
    obj_jsonfied = jsonfy_obj(data)
    return json.dumps(obj_jsonfied)
