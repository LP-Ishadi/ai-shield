from fastapi import FastAPI
import time
from shield.middleware import ShieldMiddleware

app = FastAPI()
app.add_middleware(ShieldMiddleware)

@app.post("/generate-map")
def generate_map(prompt: str):
    time.sleep(1)  # simulates a slow, expensive AI generation call
    return {"status": "success", "map_id": "12345", "prompt_received": prompt}