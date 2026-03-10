import httpx
from fastapi import APIRouter, Request, Depends, HTTPException, Response, BackgroundTasks
from src.core.security import verify_agent_token, verify_base_access
from src.core.config import AIRTABLE_PAT
from src.core.logging import log_access
router = APIRouter()
client = httpx.AsyncClient(base_url="https://api.airtable.com")

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def proxy(request: Request, path: str, background_tasks: BackgroundTasks, token_data: dict = Depends(verify_agent_token)):
    # Airtable URLs usually look like /v0/appBaseId/TableId
    parts = path.split("/")
    if len(parts) >= 2 and parts[0] == "v0":
        base_id = parts[1]
    else:
        # Fallback for meta endpoints if applicable
        base_id = parts[0] if parts else ""
        
    verify_base_access(base_id, token_data)

    url = httpx.URL(path=f"/{path}", query=request.url.query.encode("utf-8"))
    
    headers = dict(request.headers)
    headers.pop("host", None)
    headers["authorization"] = f"Bearer {AIRTABLE_PAT}"
    
    content = await request.body()
    
    try:
        req = client.build_request(
            request.method,
            url,
            headers=headers,
            content=content
        )
        resp = await client.send(req)
        
        response_headers = dict(resp.headers)
        response_headers.pop("content-length", None)
        response_headers.pop("content-encoding", None)
        
        background_tasks.add_task(log_access, token_data.get("id", "Unknown"), request.client.host if request.client else "127.0.0.1", resp.status_code, path)
        
        return Response(content=resp.content, status_code=resp.status_code, headers=response_headers)
        
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Target connection error: {exc}")
