from server_support import server, H, print_error_log
from amara.thirdparty import json
from dict_differ import DictDiffer, assert_same_jsons, pinfo

def _get_server_response(body, default=None):
    url = server() + "enrich-type"
    if default is not None:
        url += "?default=" + default
    return H.request(url, "POST", body=body)

def test_UCLA_problems():
    '''UCLA problem with "film"'''
    INPUT = {
        "id": "123",
        "sourceResource": {
            "type": "cellulose nitrate film"
        }
    }
    EXPECTED = {
        "id": "123",
        "sourceResource": {'type':'image'}
    }
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    assert_same_jsons(EXPECTED, json.loads(content))
    INPUT['sourceResource']['type'] = "nitrate film"
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    assert_same_jsons(EXPECTED, json.loads(content))
    INPUT['sourceResource']['type'] = "film"
    EXPECTED['sourceResource']['type'] = "moving image"
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    assert_same_jsons(EXPECTED, json.loads(content))

def test_type_has_priority():
    INPUT = {
        "id": "123",
        "sourceResource": {
            "type": [ {
               "text": "text",
               "attrib": {
               }
           },
           {
               "text": "text",
               "attrib": {
                   "q": "mods"
               }
           },
           {
               "text": "postcards",
               "attrib": {
                   "q": "genreform"
               }
           }
       ],
            "format":"postcard"
        }
    }
    EXPECTED = {
        "id": "123",
        "sourceResource": {"type": "text",
            "format": "postcard"}
    }
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    assert_same_jsons(EXPECTED, json.loads(content))

def test_remove_type():
    """Should remove type"""
    INPUT = {
        "id": "123",
        "sourceResource": {
            "type": "bananas"
        }
    }
    EXPECTED = {
        "id": "123",
        "sourceResource": {}
    }
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    assert_same_jsons(EXPECTED, json.loads(content))

def test_default_type():
    """Should set type to default value"""
    INPUT = {
        "id": "123",
        "sourceResource": {
            "type": "bananas"
        }
    }
    EXPECTED = {
        "id": "123",
        "sourceResource": {
            "type": "image"
        }
    }
    resp, content = _get_server_response(json.dumps(INPUT), default="image")
    assert resp.status == 200
    assert_same_jsons(EXPECTED, json.loads(content))

def test_type_for_phys_keyword():
    INPUT = {
        "id": "123",
        "sourceResource": {
            "type": "bananas",
            "format": "Holiday Card"
        }
    }
    EXPECTED = {
        "id": "123",
        "sourceResource": {
            "type": "image",
            "format": "Holiday Card"
        }
    }
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    assert_same_jsons(EXPECTED, json.loads(content))

def test_type_for_type_keyword():
    INPUT = {
        "id": "123",
        "sourceResource": {
            "type": "Photograph"
        }
    }
    EXPECTED = {
        "id": "123",
        "sourceResource": {
            "type": "image"
        }
    }
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    assert_same_jsons(EXPECTED, json.loads(content))

def test_type_for_type_keyword2():
    INPUT = {
        "id": "123",
        "sourceResource": {
            "type": "Mixed material"
        }
    }
    EXPECTED = {
        "id": "123",
        "sourceResource": {
            "type": ["image", "text"]
        }
    }
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    assert_same_jsons(EXPECTED, json.loads(content))

def test_type_set_format():
    """Format gets set correctly given invalid type value

    When send_rejects_to_format is true, format should get populated with the
    type strings that don't exactly match a valid type.
    """
    url = server() + "enrich-type?send_rejects_to_format=true"
    INPUT = {
        "sourceResource": {
            "type": "digital photograph"
        }
    }
    EXPECTED = {
        "sourceResource": {
            "type": "image",
            "format": ["digital photograph"]
        }
    }
    resp, content = H.request(url, "POST", body=json.dumps(INPUT))
    assert resp.status == 200
    assert_same_jsons(EXPECTED, json.loads(content))
    INPUT = {
        "sourceResource": {
            "type": "text"
        }
    }
    EXPECTED = {
        "sourceResource": {
            "type": "text"
        }
    }
    resp, content = H.request(url, "POST", body=json.dumps(INPUT))
    assert resp.status == 200
    assert_same_jsons(EXPECTED, json.loads(content))
    INPUT = {
        "sourceResource": {
            "type": "weird thing"
        }
    }
    EXPECTED = {
        "sourceResource": {
            "format": ["weird thing"]
        }
    }
    resp, content = H.request(url, "POST", body=json.dumps(INPUT))
    assert resp.status == 200
    assert_same_jsons(EXPECTED, json.loads(content))

def test_type_ucldc_supported():
    INPUT = {
        "id": "123",
        "sourceResource": {
            "type": "Document",
        }
    }
    EXPECTED = {
        "id": "123",
        "sourceResource": {'type':'text'}
    }
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    print "CONTENT:", content
    assert_same_jsons(EXPECTED, json.loads(content))
    INPUT = {
        "id": "123",
        "sourceResource": {
            "type": "Pamphlet",
        }
    }
    EXPECTED = {
        "id": "123",
        "sourceResource": {'type':'text'}
    }
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    print "CONTENT:", content
    assert_same_jsons(EXPECTED, json.loads(content))
    INPUT = {
        "id": "123",
        "sourceResource": {
            "type": "Newsletter",
        }
    }
    EXPECTED = {
        "id": "123",
        "sourceResource": {'type':'text'}
    }
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    print "CONTENT:", content
    assert_same_jsons(EXPECTED, json.loads(content))
    INPUT = {
        "id": "123",
        "sourceResource": {
            "type": "Essay",
        }
    }
    EXPECTED = {
        "id": "123",
        "sourceResource": {'type':'text'}
    }
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    print "CONTENT:", content
    assert_same_jsons(EXPECTED, json.loads(content))
    INPUT = {
        "id": "123",
        "sourceResource": {
            "type": "Transcript",
        }
    }
    EXPECTED = {
        "id": "123",
        "sourceResource": {'type':'text'}
    }
    resp, content = _get_server_response(json.dumps(INPUT))
    assert resp.status == 200
    print "CONTENT:", content
    assert_same_jsons(EXPECTED, json.loads(content))


if __name__ == "__main__":
    raise SystemExit("Use nosetest")
