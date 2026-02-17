import json
from urllib import request

data = {"url": "https://youtu.be/tYqehyG2K38", "lang": "es"}
req = request.Request(
    "http://127.0.0.1:5001/api/captions",
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)
resp = request.urlopen(req, timeout=120)
print("Status:", resp.status)
print(resp.read().decode("utf-8")[:1000])
