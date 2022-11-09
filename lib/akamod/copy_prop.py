from akara import logger
from akara import response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.selector import getprop, setprop, exists
from dplaingestion.utilities import iterify
from dplaingestion.utilities import load_json_body

@simple_service('POST', 'http://purl.org/la/dp/copy_prop', 'copy_prop',
    'application/json')
@load_json_body(response)
def copyprop(data, ctype, prop=None, to_prop=None, skip_if_exists=None):
    """Copies value in one prop to another prop. For use with string and/or
       list prop value types. If to_prop exists, its value is iterified then
       extended with the iterified value of prop. If the to_prop parent prop
       (ie hasView in hasView/rights) does not exist, the from_prop value is
       not copied and an error is logged.

    Keyword arguments:
    body -- the content to load
    ctype -- the type of content
    prop -- the prop to copy from (default None)
    to_prop -- the prop to copy into (default None)
    skip_if_exists -- set to True to not copy if to_prop exists
    """

    def is_string_or_list(value):
        return (isinstance(value, basestring) or isinstance(value, list))

    if (exists(data, to_prop) and skip_if_exists) or not exists(data, prop):
        pass
    else:
        if exists(data, to_prop):
            orig_value = getprop(data, prop)
            if not is_string_or_list(orig_value):
                msg = "Prop %s " % prop + \
                        "is not a string/list for record %s" % data["id"]
                logger.error(msg)
                return body

            to_value = getprop(data, to_prop)
            if not is_string_or_list(to_value):
                msg = "Prop %s " % to_prop + \
                        "is not a string/list for record %s" % data["id"]
                logger.error(msg)
                return body

            to_value = iterify(to_value)
            to_value.extend(iterify(orig_value))
            setprop(data, to_prop, to_value)
        else:
            try:
                setprop(data, to_prop, getprop(data, prop))
            except Exception, e:
                logger.error("Could not copy %s to %s: %s" %
                                (prop, to_prop, e))

    return json.dumps(data)
