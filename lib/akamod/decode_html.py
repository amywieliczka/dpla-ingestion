from akara import logger
from akara import response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.selector import exists, getprop, setprop
from dplaingestion.utilities import load_json_body
import re

@simple_service('POST', 'http://purl.org/la/dp/decode_html', 'decode_html',
                'application/json')
@load_json_body(response)
def decode_html(data, ctype, prop=None):
    """Decodes any encoded html in the prop

    Keyword arguments:
    body -- the content to load
    ctype -- the type of content
    prop -- the prop to decode
    
    """

    REGEX = ('&quot;', '"'), ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>')

    if prop and exists(data, prop):
        decoded = []
        v = getprop(data, prop)
        if not isinstance(v, list):
            v = [v]
        for s in v:
            if isinstance(s, basestring):
                for p, r in REGEX:
                    s = re.sub(p, r, s)
            decoded.append(s)

        setprop(data, prop, decoded)
                

    return json.dumps(data)
