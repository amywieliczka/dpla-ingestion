from akara import logger
from akara import response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.selector import getprop, setprop, exists, delprop
import re
from dplaingestion.utilities import load_json_body


def check_date_dict(v):

    if not isinstance(v, dict):
        return False

    return 'begin' in v and v["begin"] and 'end' in v and v["end"]


def convert(data, prop):
    value = getprop(data, prop)

    if isinstance(value, list):
        values = []
        for v in value:
            if check_date_dict(v):
                values.append(v)

        if values:
            setprop(data, prop, values)
        else:
            delprop(data, prop)

    elif not check_date_dict(value):
        delprop(data, prop)


@simple_service('POST', 'http://purl.org/la/dp/dc_clean_invalid_dates',
                'dc_clean_invalid_dates', 'application/json')
@load_json_body(response)
def dc_clean_invalid_dates(data, ctype, action="cleanup_value",
                           prop="sourceResource/date"):
        for p in prop.split(","):
            if exists(data, p):
                convert(data, p)
    else:
        logger.error("Prop param in None in %s" % __name__)

    return json.dumps(data)
