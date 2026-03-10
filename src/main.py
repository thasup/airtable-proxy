import time
from fastapi import Request, Response
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.connection import init_db
from src.routers import proxy, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Secure Proxy Server for AI Agents", lifespan=lifespan)

RATE_LIMIT_DURATION = 60
RATE_LIMIT_REQUESTS = 100
ip_history = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()
    
    if client_ip not in ip_history:
        ip_history[client_ip] = []
        
    requests = ip_history[client_ip]
    ip_history[client_ip] = [ts for ts in requests if now - ts < RATE_LIMIT_DURATION]
    
    if len(ip_history[client_ip]) >= RATE_LIMIT_REQUESTS:
        return Response(status_code=429, content="Too Many Requests")
        
    ip_history[client_ip].append(now)
    
    response = await call_next(request)
    return response

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(admin.router)
app.include_router(proxy.router)


