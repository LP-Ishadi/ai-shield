import os

# Detection thresholds — can be overridden via environment variables
COOLDOWN_SECONDS = int(os.getenv("SHIELD_COOLDOWN_SECONDS", 30))
VARIANCE_THRESHOLD = float(os.getenv("SHIELD_VARIANCE_THRESHOLD", 0.01))
REQUEST_WINDOW_SECONDS = int(os.getenv("SHIELD_REQUEST_WINDOW_SECONDS", 10))
MIN_REQUESTS_TO_CHECK = int(os.getenv("SHIELD_MIN_REQUESTS", 5))

SUSPICIOUS_USER_AGENTS = ["python-requests", "curl", "wget", "scrapy", "bot"]