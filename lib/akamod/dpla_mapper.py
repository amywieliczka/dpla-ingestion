from akara import logger, response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.create_mapper import create_mapper
from lib.utilities import load_json_body
from dplaingestion.utilities import load_json_body

@simple_service('POST', 'http://purl.org/la/dp/dpla_mapper', 'dpla_mapper',
                'application/json')
@load_json_body(response)
def dpla_mapper(data, ctype, mapper_type=None):
    if not mapper_type:
        logger.error("No mapper_type was supplied to dpla_mapper.")
    else:
        mapper = create_mapper(mapper_type, data)
        mapper.map()
        data = mapper.mapped_data

    return json.dumps(data)
