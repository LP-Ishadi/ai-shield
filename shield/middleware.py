import time
from collections import defaultdict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

request_log = defaultdict(list)
blocked_until = {}
COOLDOWN_SECONDS = 30

class ShieldMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        path = request.url.path
        # NEW: track per (IP + path) combo, not just IP alone
        key = f"{ip}:{path}"
        now = time.time()

        if key in blocked_until and now < blocked_until[key]:
            remaining = round(blocked_until[key] - now, 1)
            return JSONResponse(
                status_code=429,
                content={
                    "blocked": True,
                    "reason": f"Temporarily blocked for {remaining}s due to earlier suspicious activity on this endpoint",
                    "ip": ip
                }
            )

        request_log[key].append(now)
        request_log[key] = [t for t in request_log[key] if now - t < 10]
        recent = request_log[key]

        if len(recent) >= 5:
            gaps = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
            avg_gap = sum(gaps) / len(gaps)
            variance = sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)

            if variance < 0.01:
                blocked_until[key] = now + COOLDOWN_SECONDS
                return JSONResponse(
                    status_code=429,
                    content={
                        "blocked": True,
                        "reason": f"Detected {len(recent)} requests to {path} in 10s with suspiciously even timing (variance={variance:.4f}) — flagged as automated traffic",
                        "ip": ip
                    }
                )

        return await call_next(request)