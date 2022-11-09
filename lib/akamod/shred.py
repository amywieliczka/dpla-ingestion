import re

from akara import logger
from akara import response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.selector import getprop, setprop, exists

@simple_service('POST', 'http://purl.org/la/dp/shred', 'shred',
                'application/json')
def shred(body, ctype, action="shred", prop=None, delimiter=';', keepdup=None):
    """
    Service that accepts a JSON document and "shreds" or "unshreds" the value
    of the field(s) named by the "prop" parameter

    "prop" can include multiple property names, delimited by a comma (the delimiter
    property is used only for the fields to be shredded/unshredded). This
    requires that the fields share a common delimiter however.

    The 'shred' action splits values by delimeter. It handles some complex edge
    cases beyond what split() expects. For example:
      ["a,b,c", "d,e,f"] -> ["a","b","c","d","e","f"]
      'a,b(,c)' -> ['a', 'b(,c)']
    Duplicate values are removed unless keepdup evaluates true.

    The 'unshred' action joins a list of values with delimiter.

    See: https://issues.dp.la/issues/2940
         https://issues.dp.la/issues/4251
         https://issues.dp.la/issues/4266
         https://issues.dp.la/issues/4578
         https://issues.dp.la/issues/4600
    """
    try:
        data = json.loads(body)
    except Exception as e:
        response.code = 500
        response.add_header('content-type', 'text/plain')
        return "Unable to parse body as JSON\n" + str(e)

    def index_for_matching_close_paren(values):
        """
        Accepts a list of values. Returns the index of the index of the first 
        value containing a closing paren.
        """
        index = None
        for v in values:
            if index is not None and v.count("(") > v.count(")"):
                return index
            elif v.count(")") > v.count("("):
                index = values.index(v)
        return index

    def rejoin_partials(values, delim):
        """
        Accepts a list of values which have been split by delim. Searches for 
        values that have been separated 

        For example, this value:
          'my (somewhat contrived; value) with a delimeter enclosed in parens'
        would be split into: 
          ['my (somewhat contrived', 'value) with a delimeter enclosed in parens']
       
        This method rejoins it.
        """
        index1 = None
        index2 = None
        for v in values:
            if v.count("(") > v.count(")"):
                index1 = values.index(v)
        for v in values:
            if index2 is not None and v.count("(") > v.count(")"):
                return index2
        index_for_matching_close_paren(values)
        if index1 is not None and index2 is not None:
            if index1 == 0 and index2 == len(values) - 1:
                return [delim.join(values)]
            elif index1 == 0:
                values = [delim.join(values[:index2+1])] + values[index2+1:]
            elif index2 == len(values) - 1:
                values = values[:index1] + [delim.join(values[index1:])]
            else:
                values = values[:index1] + [delim.join(values[index1:index2+1])] + values[index2+1:]
            return rejoin_partials(values, delim)
        else:
            return values

    if not exists(data, prop):
        return json.dumps(data)

    value = getprop(data, prop)
    if isinstance(value, list):
        try:
            value = delimiter.join(value)
            value = value.replace("%s%s" % (delimiter, delimiter), delimiter)
        except Exception as e:
            logger.warn("Can't join list %s on delimiter for %s, %s" %
                        (value, data["_id"], e))

    if delimiter in value:
        setprop(data, prop, value)
    else:
        return json.dumps(data)

    shredded = [""]
    for s in re.split(re.escape(delimiter), value):
        shredded.append(s)
    shredded = rejoin_partials(shredded, delimiter)
    shredded = [i.strip() for i in shredded if i.strip()]

    result = []
    for s in shredded:
        if s not in result:
            result.append(s)
    shredded = result
    setprop(data, prop, shredded)

    return json.dumps(data)
