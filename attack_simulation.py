import requests
import time

url = "http://127.0.0.1:8000/generate-map"

for i in range(10):
    response = requests.post(url, params={"prompt": "test"})
    print(f"Request {i+1}: {response.status_code} - {response.json()}")
    time.sleep(0.5)  # perfectly even 0.5s gap every time — this is what makes it look robotic