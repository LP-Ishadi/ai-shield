import requests
import time

url = "http://127.0.0.1:8001/rest/products/search"

for i in range(10):
    response = requests.get(url, params={"q": "test"})
    print(f"Request {i+1}: {response.status_code}")
    time.sleep(0.5)