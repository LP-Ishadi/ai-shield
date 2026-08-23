import time
from collections import defaultdict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

request_log = defaultdict(list)
blocked_until = {}  # NEW: tracks "this IP is blocked until this timestamp"
COOLDOWN_SECONDS = 30  # how long an IP stays blocked after being flagged

class ShieldMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        now = time.time()

        # STEP 1: check if this IP is currently in a cooldown/timeout
        if ip in blocked_until and now < blocked_until[ip]:
            remaining = round(blocked_until[ip] - now, 1)
            return JSONResponse(
                status_code=429,
                content={
                    "blocked": True,
                    "reason": f"IP is temporarily blocked for {remaining}s due to earlier suspicious activity",
                    "ip": ip
                }
            )

        # STEP 2: normal timing check (same as before)
        request_log[ip].append(now)
        request_log[ip] = [t for t in request_log[ip] if now - t < 10]
        recent = request_log[ip]

        if len(recent) >= 5:
            gaps = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
            avg_gap = sum(gaps) / len(gaps)
            variance = sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)

            if variance < 0.01:
                # NEW: put this IP into cooldown instead of just blocking once
                blocked_until[ip] = now + COOLDOWN_SECONDS
                return JSONResponse(
                    status_code=429,
                    content={
                        "blocked": True,
                        "reason": f"Detected {len(recent)} requests in 10s with suspiciously even timing (variance={variance:.4f}) — flagged as automated traffic. IP blocked for {COOLDOWN_SECONDS}s.",
                        "ip": ip
                    }
                )

        return await call_next(request)