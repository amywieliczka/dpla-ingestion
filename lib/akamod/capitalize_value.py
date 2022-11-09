from akara import logger
from akara import response
from akara.services import simple_service
from amara.thirdparty import json

from dplaingestion.selector import getprop, setprop, exists
from dplaingestion.utilities import load_json_body
from lib.utilities import apply_to_leaves_two_layers


# Below fields should have removed do at the end.
DEFAULT_PROP = [
    "sourceResource/language",
    "sourceResource/title",
    "sourceResource/rights",
    "sourceResource/creator",
    "sourceResource/relation",
    "sourceResource/publisher",
    "sourceResource/subject",
    "sourceResource/description",
    "sourceResource/collection/title",
    "sourceResource/contributor",
    "sourceResource/extent",
    "sourceResource/format",
    # "sourceResource/spatial/currentLocation",  # State Located In
    # "sourceResource/spatial",  # place name?
    "dataProvider",
    "provider/name"
]

@simple_service('POST', 'http://purl.org/la/dp/capitalize_value', 'capitalize_value', 'application/json')
@load_json_body(response)
def capitalize_value(data, ctype, prop=",".join(DEFAULT_PROP), exclude=None):
    """
    Service that accepts a JSON document and capitalizes the prop field of that document
    """
    props = prop.split(",")
    if exclude in props:
        prop.remove(exclude)

    for prop in props:
        data_value = getprop(data, prop, keyErrorAsNone=True)
        if not data_value:
            continue

        new_data_value = apply_to_leaves_two_layers(
            data_value, lambda s: s[0].upper() + s[1:])

        setprop(data, prop, new_data_value)

    return json.dumps(data)
