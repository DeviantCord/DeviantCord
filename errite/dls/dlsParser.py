import urllib
import json

def getTokenResponse(hostname:str, username:str, password:str):
    tokenRequestURL = hostname + "/get_token/" + username + "/" + password + "/deviantcordbot"
    with urllib.request.urlopen(tokenRequestURL) as url:
        data = json.loads(url.read().decode())
        return data;
def getShardResponse(hostname:str, token:str, shard_type:str):
    shardRequestURL = str(hostname + "/get_shard/" + token + "/" + shard_type)
    with urllib.request.urlopen(shardRequestURL) as url:
        data = json.loads(url.read().decode())
        return data;