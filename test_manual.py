import urllib.request
import json

url_extract = "http://127.0.0.1:8000/extract"
url_retrieve = "http://127.0.0.1:8000/sentinel/retrieve"
session_id = "test_manual_123"

# Create session
req1 = urllib.request.Request(url_extract, data=json.dumps({"session_id": session_id, "text": "dummy"}).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
urllib.request.urlopen(req1)

# Retrieve
payload = {
    "session_id": session_id,
    "product_name": "Carbon Steel Flat Bars", 
    "hs_code": "7214.20.00", 
    "import_country": "Malaysia", 
    "export_country": "China"
}
req2 = urllib.request.Request(url_retrieve, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req2) as response:
        print("Status:", response.status)
        print("Body:", json.loads(response.read().decode('utf-8')))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Body:", e.read().decode('utf-8'))
