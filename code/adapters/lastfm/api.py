import urllib2
from urllib import urlencode
import json
from api_key import api_key

api_url = "http://ws.audioscrobbler.com/2.0/"

def gettoptags(mbid, api_key=api_key):
    resp = call("artist.gettoptags", {"mbid":mbid})
    if resp and resp.has_key("toptags") and resp["toptags"].has_key("tag"):
        return resp["toptags"]["tag"]
    
    raise Exception("Invalid Response")

def call(method, params, api_key=api_key):
    params = params or {}
    params["method"] = method
    params["api_key"] = api_key
    params["api_key"] = api_key
    params["format"] = "json" 

    url = api_url +"?"+ urlencode(params);

    req = urllib2.urlopen(url)
    return json.load(req)
