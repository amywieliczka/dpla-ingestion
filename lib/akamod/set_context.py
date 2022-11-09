from akara import response
from amara.thirdparty import json
from akara.services import simple_service
from dplaingestion.selector import setprop
from dplaingestion.utilities import load_json_body

@simple_service('POST', 'http://purl.org/la/dp/set_context',
                'set_context', 'application/json')
@load_json_body(response)
def setcontext(data, ctype, prop="@context"):
    """   
    Service that accepts a JSON document and sets the "@context" field of that
    document.
    """

    item_context = {
        "@context": "http://dp.la/api/items/context",
        "aggregatedCHO": "#sourceResource",
        "@type": "ore:Aggregation"
    }

    collection_context = {
        "@context": "http://dp.la/api/collections/context",
        "@type": "dcmitype:Collection" 
    }

    if data["ingestType"] == "item":
        data.update(item_context)
        setprop(data, "sourceResource/@id", "%s#sourceResource" % data["@id"])
    else:
        data.update(collection_context)

    return json.dumps(data)
