import urllib.request
import json

url = "http://127.0.0.1:8000/sentinel/retrieve"
payload = {
    "session_id": "test_isolated_005",
    "product_name": "Carbon Steel Flat Bars", 
    "hs_code": "7214.20.00", 
    "import_country": "Malaysia", 
    "export_country": "China"
}

req = urllib.request.Request(
    url, 
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Body:", json.loads(response.read().decode('utf-8')))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Body:", e.read().decode('utf-8'))
