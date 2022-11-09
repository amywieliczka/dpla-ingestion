from akara import logger
from akara import response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.selector import getprop, setprop, delprop, exists
from dplaingestion.utilities import iterify
import re
from dplaingestion.utilities import load_json_body

@simple_service('POST', 'http://purl.org/la/dp/move_date_values',
                'move_date_values', 'application/json')
@load_json_body(response)
def movedatevalues(data, ctype, action="move_date_values", prop=None,
                   to_prop="sourceResource/temporal"):
    """
    Service that accepts a JSON document and moves any dates found in the prop
    field to the temporal field.
    """

    if not prop:
        logger.error("Prop param is None in %s" % __name__)
        return 

    REGSEARCH = [
        "\d{1,4}\s*[-/]\s*\d{1,4}\s*[-/]\s*\d{1,4}\s*[-/]\s*\d{1,4}\s*[-/]\s*\d{1,4}\s*[-/]\s*\d{1,4}",
        "\d{1,2}\s*[-/]\s*\d{4}\s*[-/]\s*\d{1,2}\s*[-/]\s*\d{4}",
        "\d{4}\s*[-/]\s*\d{1,2}\s*[-/]\s*\d{4}\s*[-/]\s*\d{1,2}",
        "\d{1,4}\s*[-/]\s*\d{1,4}\s*[-/]\s*\d{1,4}",
        "\d{4}\s*[-/]\s*\d{4}",
        "\d{1,2}\s*[-/]\s*\d{4}",
        "\d{4}\s*[-/]\s*\d{1,2}",
        "\d{4}s?",
        "\d{1,2}\s*(?:st|nd|rd|th)\s*century",
        ".*circa.*",
        ".*[pP]eriod(?!.)"
        ]

    def cleanup(s):
        s = re.sub("[\(\)\.\?]", "",s)
        return s.strip()


    if exists(data, prop):
        values = iterify(getprop(data, prop))
        remove = []
        toprop = iterify(getprop(data, to_prop)) if exists(data, to_prop) \
                 else []

        for v in iterify(values):
            if isinstance(v, basestring):
                c = cleanup(v)
                for pattern in REGSEARCH:
                    m = re.compile(pattern, re.I).findall(c)
                    if len(m) == 1 and not re.sub(m[0], "", c).strip():
                        if m[0] not in toprop:
                            toprop.append(m[0])
                        # Append the non-cleaned value to remove
                        remove.append(v)
                        break

        if toprop:
            setprop(data, to_prop, toprop)
            if len(values) == len(remove):
                delprop(data, prop)
            else:
                setprop(data, prop, [v for v in values if v not in remove])


    return json.dumps(data)
