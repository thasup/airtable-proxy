# Secure Airtable Proxy for AI Agents

A secure, high-performance proxy server built with FastAPI that sits between your AI agents and the Airtable API. The server acts as a centralized gateway to manage authentication, enforce access scopes, and completely isolate your proprietary Airtable Personal Access Tokens (PAT) from the public internet and external agents.

## Why this Proxy?

When building and deploying AI agents (especially autonomous or third-party ones), granting direct access to your primary Airtable tokens poses a massive security risk. Instead of distributing your secret token, this proxy allows you to:
- Issue unique, trackable **sub-tokens** to specific AI agents.
- **Scope** those tokens to have access ONLY to specific Airtable Bases.
- **Revoke** an agent's token in real-time without rotating your master Airtable PAT.
- **Rate Limit** unauthorized requests and protect your upstream API limits from brute-force scripts.
- **Audit** and log all requests internally in an embedded SQLite database.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- An [Airtable Personal Access Token (PAT)](https://airtable.com/create/tokens)

### 1. Installation

Clone the repository and install the minimal dependencies inside a virtual environment:

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file or export the following environment variables. The server reads these on startup:

```env
# REQUIRED: Your actual Airtable token (kept purely server-side)
AIRTABLE_PAT=patYourAirtableTokenSecret123

# REQUIRED: A strong passphrase to protect the Proxy's Admin API
ADMIN_SECRET=your_super_secret_admin_phrase

# OPTIONAL: Path to store your SQLite database (defaults to proxy.db)
DB_PATH=proxy.db
```

### 3. Running the Server

You can use the provided convenience script to instantly boot the server:

```bash
chmod +x run.sh
./run.sh
```

Alternatively, run the ASGI server directly:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```
*The proxy will automatically detect the lack of a database and initialize the credentials and logs tables securely.*

---

## 🔑 Administering AI Agent Tokens

To allow an AI agent to use your proxy, you first need to mint them an access token. Because the admin routes are secured, you must provide the `ADMIN_SECRET` bearer token you configured on startup.

### Generating a New Token

**Request:**
```bash
curl -X POST "http://localhost:8000/admin/tokens" \
     -H "Authorization: Bearer your_super_secret_admin_phrase" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Customer Support Agent",
           "allowed_bases": ["appXYZ123", "appABC789"]
         }'
```
*(Tip: Pass `["*"]` if you want the agent to have access to all bases the master PAT can access).*

**Response:**
```json
{
  "id": "b3e945...",
  "token": "sk_agent_xxxxxxxxxxx",
  "name": "Customer Support Agent",
  "allowed_bases": ["appXYZ123", "appABC789"],
  "created_at": "2026-03-11T00:00:00Z",
  "is_active": true
}
```
**🚨 IMPORTANT:** The `token` string is only returned *once*. Internally, the proxy stores a one-way `SHA-256` hash. Provide this `sk_agent_` token to your AI agent.

### Revoking a Token

If an agent goes rogue or the token leaks, instantly revoke access via the Admin API using the database `id`:

```bash
curl -X DELETE "http://localhost:8000/admin/tokens/b3e945..." \
     -H "Authorization: Bearer your_super_secret_admin_phrase"
```

---

## 🤖 AI Agent Proxy Usage

To interact with Airtable data, the AI agent simply sends standard API requests to your proxy URL instead of `api.airtable.com`.

All endpoints are fully supported (e.g. `GET`, `POST`, `PATCH`, `DELETE`). The proxy parses the `baseId`, validates the token's active status and base permissions in under `<50ms`, replaces the authentication header, and forwards the exact payload to Airtable.

**Example Request from the AI Agent:**
```bash
curl -X GET "http://localhost:8000/v0/appXYZ123/Table1" \
     -H "Authorization: Bearer sk_agent_xxxxxxxxxxx"
```

If the token is invalid, revoked, or attempts to access a Base it doesn't have permission for, the proxy intercepts and immediately rejects the request with a `401` or `403` status without hitting the upstream Airtable API.

---

## 🛡 Security & Concurrency Specs
- **Data Model:** Tokens and Access Logs are managed via a local `SQLite` file ensuring minimal external network dependencies and reducing the attack surface.
- **Rate-Limiting:** Incorporates an in-memory sliding window rate-limiter rejecting IPs executing excessively rapid or brute-force requests (`429 Too Many Requests`).
- **Asynchronous & Highly Concurrent:** Powered by `FastAPI` and `httpx`, ensuring high performance and non-blocking background I/O capable of handling hundreds of concurrent agent requests efficiently.
- **Audit Logging:** Every authenticated access attempt is catalogged (timestamp, success code, and requested path) alongside the unique agent ID utilizing background threads.

## 🧪 Testing
The proxy includes integration tests for both the Proxy routes and Admin routing checks manually confirming authentication behavior:
```bash
pytest
```

---

## 🌍 Deployment

Since the proxy server is handling sensitive authentication tokens over the internet, **HTTPS is heavily recommended** for production environments to prevent man-in-the-middle token leakage.

### Standard Production Setup

A typical production setup involves running the app using a process manager or a container, and placing it behind a reverse proxy (like Nginx, Caddy, or Traefik) that handles SSL/TLS termination.

**Running with Uvicorn in Production:**
To fully utilize modern server architectures, run `uvicorn` with multiple workers:
```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000 --workers 4
```
*(Note: Since SQLite is using a local file, ensure that multiple workers aren't causing write concurrency issues for your workload. Setting `check_same_thread=False` generally mitigates read limitations, and token creation is infrequent).*

**Caddy Reverse Proxy Example (`Caddyfile`):**
Caddy automatically handles Let's Encrypt HTTPS generation:
```text
proxy.yourdomain.com {
    reverse_proxy 127.0.0.1:8000
}
```

### Docker Deployment

If you prefer containerized deployment, you can scaffold a container rapidly:

**1. Create a `Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. Build & Run (Mounting the DB to preserve secrets state):**
```bash
docker build -t airtable-proxy .

docker run -d -p 8000:8000 \
  -e AIRTABLE_PAT="patYourAirtableTokenSecret123" \
  -e ADMIN_SECRET="your_super_secret_admin_phrase" \
  -v $(pwd)/proxy.db:/app/proxy.db \
  airtable-proxy
```
