import re
import os

from akara import logger
from akara import response
from akara.services import simple_service
from amara.thirdparty import json
from dplaingestion.selector import delprop, getprop, setprop, exists
from amara.lib.iri import is_absolute
from dplaingestion.utilities import load_json_body


@simple_service('POST', 'http://purl.org/la/dp/enrich-format', 'enrich-format',
                'application/json')
@load_json_body(response)
def enrichformat(data, ctype, action="enrich-format",
                 prop="sourceResource/format",
                 type_field="sourceResource/type"):
    """
    Service that accepts a JSON document and enriches the "format" field of
    that document by: 

    a) Setting the format to be all lowercase
    b) Running through a set of cleanup regex's (e.g. image/jpg -> image/jpeg)
    c) Checking to see if the field is a valid IMT
       See http://www.iana.org/assignments/media-types for list of valid
       media-types. We require that a subtype is defined.
    d) Removing any extra text after the IMT
    e) Moving valid IMT values to hasView/format if hasView exists and
       its format is not set
    f) Setting type field from format field, if it is not set. The format field
       is taken if it is a string, or the first element if it is a list. It is
        then split and the first part of IMT is taken.

    By default works on the 'sourceResource/format' field but can be overridden
    by passing the name of the field to use as the 'prop' parameter.
    """

    FORMAT_2_TYPE_MAPPINGS = {
        "audio": "sound",
        "image": "image",
        "video": "moving image",
        "text": "text"
    }

    REGEXPS = ('audio/mp3', 'audio/mpeg'), ('images/jpeg', 'image/jpeg'), \
              ('image/jpg', 'image/jpeg'), ('image/jp$', 'image/jpeg'), \
              ('img/jpg', 'image/jpeg'), ('^jpeg$', 'image/jpeg'), \
              ('^jpg$', 'image/jpeg'), ('\W$', '')
    IMT_TYPES = ['application', 'audio', 'image', 'message', 'model',
                 'multipart', 'text', 'video']

    def is_imt(cleaned_format):
        imt_regexes = [re.compile('^' + x + '(/)') for x in IMT_TYPES]
        return any(regex.match(cleaned_format) for regex in imt_regexes)

    if not exists(data, prop):
        return json.dumps(data)

    record_formats = getprop(data, prop)
    if isinstance(record_formats, basestring):
        record_formats = [record_formats]

    imt_values = []
    mapped_format = []

    for record_format in record_formats:
        if record_format.startswith("http") and is_absolute(record_format):
            ext = os.path.splitext(record_format)[1].split('.')
            record_format = ext[1] if len(ext) == 2 else ""
            
        cleaned_format = record_format.lower().strip()
        for pattern, replace in REGEXPS:
            cleaned_format = re.sub(pattern, replace, cleaned_format)
            cleaned_format = re.sub(r"^([a-z0-9/]+)\s.*",r"\1", cleaned_format)

        if is_imt(cleaned_format):
            # Append IMT values to mapped_format
            if cleaned_format not in mapped_format:
                mapped_format.append(cleaned_format)

            # Append to imt_values for use in type
            if cleaned_format not in imt_values:
                imt_values.append(cleaned_format)

        else:
            # Retain non-IMT values in sourceResource/format, non-cleaned
            if record_format not in mapped_format:
                mapped_format.append(record_format)

    if mapped_format:
        if len(mapped_format) == 1:
            mapped_format = mapped_format[0]
        setprop(data, prop, mapped_format)
    else:
        delprop(data, prop)

    if (exists(data, "hasView") and 
            not exists(data, "hasView/format") and 
            imt_values):
        hasview_format = imt_values
        if len(hasview_format) == 1:
            hasview_format = hasview_format[0]
        setprop(data, "hasView/format", hasview_format)

    # Setting the type if it is empty.
    if not exists(data, type_field) and imt_values:
        type = []
        for imt in imt_values:
            t = getprop(FORMAT_2_TYPE_MAPPINGS, imt.split("/")[0], True)
            if t and t not in type:
                type.append(t)

        if type:
            if len(type) == 1:
                type = type[0]
            setprop(data, type_field, type)

    return json.dumps(data)
