from akara import logger
from akara import response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.selector import getprop, setprop, exists
from utilities import load_json_body
import re

@simple_service('POST', 'http://purl.org/la/dp/enrich-subject', 'enrich-subject', 'application/json')
@load_json_body(response)
def enrichsubject(data,ctype,action="enrich-subject",prop="sourceResource/subject"):
    '''   
    Service that accepts a JSON document and enriches the "subject" field of that document
    by: 

    a) converting converting subjects that are raw strings to dictionaries of the form: { name: <subject> }
    b) applying a set of regexps to do data cleanup
    
    By default works on the 'subject' field, but can be overridden by passing the name of the field to use
    as a parameter
    '''   
    
    regexps = ('\s*-{2,4}\s*', '--'), \
              ('\s*-\s*-\s*', '--'), \
              ('^[\.\' ";]*', ''), \
              ('[\.\' ";]*$','')

    def cleanup(s):
        if isinstance(s, dict):
            #already {'name': <val>}
            s = s['name']

        s = s.strip()
        for pattern, replace in regexps:
            s = re.sub(pattern, replace, s)
        s = s[:1].upper() + s[1:]
        return s

    if exists(data,prop):
        value = getprop(data,prop)
        subject = []
        if isinstance(value, basestring):
            value = [value]
        for s in value:
            subj = cleanup(s)
            if subj:
                subject.append({ "name" : subj })

        setprop(data,prop,subject)

    return json.dumps(data)
