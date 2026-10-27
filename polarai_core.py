import json
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

def _base(url):
    value=url.strip().rstrip("/")
    u=urlsplit(value)
    if u.scheme not in ("http","https") or u.hostname not in ("localhost","127.0.0.1","::1"):
        raise ValueError("Usa un server locale (127.0.0.1 o localhost)")
    if u.username or u.password or u.fragment or u.query:
        raise ValueError("URL del server non valido")
    return value if value.endswith("/v1") else value+"/v1"

def _call(url,endpoint,payload=None):
    data=None if payload is None else json.dumps(payload).encode("utf-8")
    req=Request(_base(url)+endpoint,data=data,headers={"Content-Type":"application/json"},method="POST" if data else "GET")
    with urlopen(req,timeout=120) as response:
        return json.load(response)

def list_models(url):
    return [entry["id"] for entry in _call(url,"/models").get("data",[]) if "id" in entry]

def generate(url,model,system,prompt):
    result=_call(url,"/chat/completions",{"model":model,"messages":[{"role":"system","content":system},{"role":"user","content":prompt}],"stream":False})
    return result["choices"][0]["message"]["content"]


def generate_messages(url,model,messages):
    result=_call(url,"/chat/completions",{"model":model,"messages":messages,"stream":False,"temperature":0.1})
    return result["choices"][0]["message"]["content"]
