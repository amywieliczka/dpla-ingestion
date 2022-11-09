from akara import logger, response, module_config
from akara.services import simple_service
from amara.thirdparty import json
import dplaingestion.itemtype as itemtype
from utilities import load_json_body

type_for_type_keyword = \
        module_config('enrich_type').get('type_for_ot_keyword')
type_for_format_keyword = \
        module_config('enrich_type').get('type_for_phys_keyword')

@simple_service('POST', 'http://purl.org/la/dp/enrich-type', 'enrich-type',
                'application/json')
@load_json_body(response)
def enrichtype(data, ctype,
               action="enrich-type",
               prop="sourceResource/type",
               format_field="sourceResource/format",
               default=None,
               send_rejects_to_format=False):
    """
    Service that accepts a JSON document and enriches the "type" field of that
    document by:

    By default works on the 'type' field, but can be overridden by passing the
    name of the field to use as a parameter.

    A default type, if none can be determined, may be specified with the
    "default" querystring parameter.  If no default is given, the type field
    will be unmodified, or not added, in the result.
    """
    global type_for_type_keyword, type_for_format_keyword

    # normalize type data structure
    sr_type = data.get('sourceResource', {'type': []}).get('type')
    if not isinstance(sr_type, list):
        sr_type = [sr_type]
    sr_type = [
        t.get('#text', t.get('text')) 
        if isinstance(t, dict) else t 
        for t in sr_type
    ]

    # normalize format data structure
    sr_format = data.get('sourceResource', {'format': []}).get('format')
    if not isinstance(sr_format, list):
        sr_format = [sr_format]
    

    if not sr_type or not sr_format:
        logger.warning(
            'enrich-type lacks sourceResource for _id ' + 
            data.get('_id', '[no id]')
        )
        return json.dumps(data)

    type_strings = [t.lower() for t in sr_type]
    format_strings = [f.lower() for f in sr_format]

    try:
        data['sourceResource']['type'] = \
                itemtype.type_for_strings_and_mappings([
                    (type_strings, type_for_type_keyword),
                    (format_strings, type_for_format_keyword),
                ])
    except itemtype.NoTypeError:
        logger.warning('Can not deduce type for item with _id: %s' % \
                       data.get('_id', '[no id]'))
        if default:
            data['sourceResource']['type'] = default
        else:
            try:
                del data['sourceResource']['type']
            except:
                pass

    return json.dumps(data)
