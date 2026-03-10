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

### 🚀 Render Web Service (Free Tier)

This repository comes pre-configured for a frictionless deployment to [Render's Free Tier](https://render.com/).

**Important Note for Free Tiers**: Render's free tier heavily relies on ephemeral storage. Any local files, including the SQLite database, will be **lost/wiped** whenever the service automatically spins down (due to inactivity) or restarts. Because of this, it is recommended to manage tokens externally or accept that you will need to re-issue them if using the free web tier.

**Automated Deployment via `render.yaml`:**
1. Connect your Github/GitLab account to Render.
2. Under "Blueprints", click "New Blueprint Instance".
3. Select this repository.
4. Render will automatically parse the `render.yaml` file configuring the build and start commands dynamically. 
5. In the Render Dashboard under your new Web Service, manually supply your secrets for `AIRTABLE_PAT` and `ADMIN_SECRET` directly in the environment variables tab. 

**Manual Setup Instructions:**
1. In the Render Dashboard, click "New" -> "Web Service".
2. Select your repository.
3. Configure the following specific fields:
   * **Language**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
4. Under "Environment Variables", manually enter:
   * `AIRTABLE_PAT` = your production Airtable PAT
   * `ADMIN_SECRET` = your proxy admin secret phrase
   * `DB_PATH` = `/tmp/proxy.db` (Write permission target for Render)
   * `PYTHON_VERSION` = `3.11.0`

Once provisioned, your AI Agents can immediately start sending authenticated Bearer requests to `https://your-app-slug.onrender.com/*`.
