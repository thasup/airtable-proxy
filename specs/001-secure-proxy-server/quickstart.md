# Quickstart

## Prerequisites
- Python 3.11+
- Airtable PAT (Personal Access Token) with necessary data/read/write scopes.

## Setup
1. Clone the repository to the designated server.
2. Initialize virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install minimal required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file referencing the Airtable PAT to be stored purely server-side:
   ```env
   # The centralized server token
   AIRTABLE_PAT=patXYZ_your_airtable_token

   # A secure key for the server admin to manage agents
   ADMIN_SECRET=your_admin_secret_string

   # The storage directory for the SQLite agent DB
   DB_PATH=./proxy.db
   ```
5. SQLite will initialize tables continuously upon optimal first boot.

## Running
Run the high-concurrency FastAPI asynchronous gateway (exposing to internet):

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## AI Agent Integration Usage
Supply the external or local AI agent with an independently generated bearer token. Once generated via the `/admin/tokens` endpoint, the agent seamlessly sends requests towards the proxy rather than directly towards Airtable:

### Request Example
```bash
curl -X GET "http://[your-proxy-host]:8000/v0/appXYZ123/Table1" \
     -H "Authorization: Bearer sk_agent_abc123..."
```

*(This proxy validates the token's active status and base access in `< 50ms` prior to appending the actual Airtable PAT securely upstream.)*
