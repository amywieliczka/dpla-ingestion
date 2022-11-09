from akara import logger
from akara import response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.selector import getprop, setprop, exists
import re
from dplaingestion.utilities import load_json_body

from lib.utilities import apply_to_leaves_two_layers


def cleanup(value, prop):
    """ Performs a cleanup of value using a bunch of regexps.

    Arguments:
        value - string for convertion

    Returns:
        Converted string.
    """
    # Do not remove double quotes from title
    dquote = '' if prop == "sourceResource/title" or prop == "sourceResource/description" else '"'

    # Remove dot at the end if field name is not in the
    # DONT_STRIP_DOT_END table.
    with_dot = '' if prop in DONT_STRIP_DOT_END else "\."

    # Tags for stripping at beginning and at the end.
    lead_strip = '[%s\' \r\t\n;,%s]*' % ("\.", dquote)
    trail_strip = '[%s\' \r\t\n;,%s]*' % (with_dot, dquote)

    REGEXPS = ('\( ', '('), \
              (' \)', ')'), \
              (' *-- *', '--'), \
              ('[\t ]{2,}', ' '), \
              ('^' + lead_strip, ''), \
              (trail_strip + '$', '')

    value = value.strip()
    for pattern, replace in REGEXPS:
        value = re.sub(pattern, replace, value)

    return value


"""
Fields which should not be changed:
-- format (there are often dimensions in this field)
-- extent (for the same reason)
-- descriptions (full text, includes sentences)
-- rights (full text, includes sentences)
-- place (may end in an abbreviated state name)

"""
DONT_STRIP_DOT_END = [
    "hasView/format", "sourceResource/format", "sourceResource/extent",
    "sourceResource/rights",
    "sourceResource/place", "sourceResource/collection/title"
]

# Below fields should have removed do at the end.
DEFAULT_PROP = [
    "sourceResource/language", "sourceResource/title",
    "sourceResource/creator", "sourceResource/relation",
    "sourceResource/publisher", "sourceResource/subject",
    "sourceResource/date",
    "sourceResource/collection/title", "sourceResource/collection/description",
    "sourceResource/contributor", "sourceResource/spatial/name"
]


@simple_service('POST', 'http://purl.org/la/dp/cleanup_value', 'cleanup_value',
                'application/json')
@load_json_body(response)
def cleanup_value(data,
                  ctype,
                  action="cleanup_value",
                  prop=",".join(DEFAULT_PROP + DONT_STRIP_DOT_END)):
    '''
    Service that accepts a JSON document and enriches the prop field of that document by:

    a) applying a set of regexps to do data cleanup
    '''
    props = prop
    for prop in props.split(","):
        if exists(data, prop):
            data_value = getprop(data, prop)
            new_data_value = apply_to_leaves_two_layers(
                data_value, cleanup, prop)
            setprop(data, prop, new_data_value)

    return json.dumps(data)
