from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx
from shield.middleware import ShieldMiddleware

app = FastAPI()
app.add_middleware(ShieldMiddleware)

@app.api_route("/{path:path}", methods=["GET", "POST"])
async def proxy(path: str, request: Request):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        url = f"http://localhost:3000/{path}"
        forward_headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in ("host", "accept-encoding")
        }
        resp = await client.request(
            request.method,
            url,
            headers=forward_headers,
            params=request.query_params,
            content=await request.body(),
        )
        excluded_headers = {"content-encoding", "content-length", "transfer-encoding", "connection"}
        response_headers = {
            k: v for k, v in resp.headers.items()
            if k.lower() not in excluded_headers
        }
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=response_headers,
            media_type=resp.headers.get("content-type"),
        )