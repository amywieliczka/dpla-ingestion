from akara import logger
from akara import response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.selector import getprop, setprop, delprop
from dplaingestion.utilities import load_json_body

@simple_service("POST", "http://purl.org/la/dp/remove_list_values",
                "remove_list_values", "application/json")
@load_json_body(response)
def remove_list_values(data, ctype, prop=None, values=None):
    """Given a comma-separated string of values, removes any instance of each
       value from the prop.
    """
    v = getprop(data, prop, True)
    
    if isinstance(v, list) and values is not None:
        values = values.split(",")
        v = [s for s in v if s not in values]
        if v:
            setprop(data, prop, v)
        else:
            delprop(data, prop)

    return json.dumps(data)
