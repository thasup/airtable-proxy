# Airtable API Proxy Server

A simple Python proxy server that forwards requests from clients (or LLMs) to the Airtable Web API, automatically attaching the correct authentication header.

---

## 1. Project Overview

### Why a Proxy?

- **Security**: Keep your Airtable Personal Access Token (PAT) on the server.
- **Simplicity**: LLMs/clients call your proxy; they don’t need to know Airtable auth.
- **Flexibility**: Easy place to add rate limiting, logging, transformations, etc.

### What This Proxy Does

- Exposes endpoints under `/v0/...` that mirror Airtable’s `/v0/...` API.
- Adds `Authorization: Bearer <AIRTABLE_TOKEN>` to every outgoing request.
- Forwards method, path, query params, and JSON body to Airtable.
- Returns Airtable’s response (status code + body) to the caller.

---

## 2. Airtable API Quick Reference

### Base URL

```text
https://api.airtable.com/v0/
```

### Authentication

All requests require a Bearer token in the `Authorization` header:

```text
Authorization: Bearer YOUR_PERSONAL_ACCESS_TOKEN
```

### Common Endpoints

| Method | Endpoint                                | Description      |
| ------ | --------------------------------------- | ---------------- |
| GET    | `/v0/{baseId}/{tableName}`             | List records     |
| GET    | `/v0/{baseId}/{tableName}/{recordId}`  | Get a record     |
| POST   | `/v0/{baseId}/{tableName}`             | Create records   |
| PATCH  | `/v0/{baseId}/{tableName}`             | Update records   |
| DELETE | `/v0/{baseId}/{tableName}`             | Delete records   |

### Getting Your PAT

1. Go to <https://airtable.com/create/tokens>
2. Click **"Create token"**
3. Add scopes (for example: `data.records:read`, `data.records:write`)
4. Add the bases/workspaces you want to access
5. Copy the token (you only see it once!)

---

## 3. Tech Stack

| Component        | Choice        | Why                                   |
| ---------------- | ------------- | ------------------------------------- |
| Web framework    | Flask         | Simple, beginner-friendly             |
| HTTP client      | `requests`    | Popular, intuitive API                |
| Config           | `python-dotenv` | Load `.env` (similar to JS dotenv) |
| Prod server      | `gunicorn`    | WSGI server for deployment (Render)   |

---

## 4. Project Structure

```text
airtable-proxy/
├── app.py           # Main Flask application (proxy logic)
├── requirements.txt # Dependencies
├── render.yaml      # Render deployment config
├── .env.example     # Example environment variables (no secrets)
├── .gitignore       # Ignore venv, __pycache__, .env, etc.
├── PLAN.md          # Original learning-focused project plan
└── README.md        # This file
```

---

## 5. Setup & Local Development

### 5.1. Prerequisites

- Python 3.10+ installed
- PowerShell or any terminal

### 5.2. Create and Activate Virtual Environment

```bash
# From project root
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 5.3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5.4. Configure Environment Variables

Create a `.env` file (do **not** commit this):

```text
AIRTABLE_TOKEN=pat.xxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Or copy from `.env.example` and edit:

```bash
copy .env.example .env   # Windows
# then open .env and paste your real PAT
```

---

## 6. Running the Server Locally

From the project root with the virtual environment active:

```bash
python app.py
```

You should see something like:

```text
==================================================
Airtable Proxy Server
==================================================
Token configured: True
Starting server on http://localhost:5000
==================================================
```

The server will be available at:

- <http://localhost:5000/>

---

## 7. Using the Proxy

### 7.1. Health Check

```bash
curl http://localhost:5000/
```

Example response:

```json
{
  "status": "ok",
  "message": "Airtable Proxy Server is running",
  "token_configured": true
}
```

### 7.2. List Bases (Airtable Metadata API)

```bash
curl "http://localhost:5000/v0/meta/bases"
```

In PowerShell:

```powershell
(Invoke-RestMethod "http://localhost:5000/v0/meta/bases").bases | Format-Table id, name
```

### 7.3. List Tables in a Base

```bash
curl "http://localhost:5000/v0/meta/bases/{baseId}/tables"
```

PowerShell example for a specific base:

```powershell
(Invoke-RestMethod "http://localhost:5000/v0/meta/bases/appoPztPp3kjnaI4Q/tables").tables | Format-Table id, name
```

### 7.4. List Records from a Table

```bash
curl "http://localhost:5000/v0/{baseId}/{tableName}?maxRecords=3"
```

Example (School of Lifelong Learning → `Books`):

```bash
curl "http://localhost:5000/v0/appoPztPp3kjnaI4Q/Books?maxRecords=3"
```

### 7.5. Create Records

```bash
curl -X POST "http://localhost:5000/v0/{baseId}/{tableName}" \
  -H "Content-Type: application/json" \
  -d '{"records": [{"fields": {"Name": "Test"}}]}'
```

### 7.6. Filter with `filterByFormula`

```bash
curl "http://localhost:5000/v0/{baseId}/{tableName}?filterByFormula={Status}='Finished'"
```

(Remember to URL-encode complex formulas when needed.)

---

## 8. How the Proxy Works (Code Overview)

High-level flow in `app.py`:

1. **Load config** from `.env` using `python-dotenv`.
2. **Create** a Flask app.
3. `/` route → health check.
4. `/v0/<path:path>` route → catch-all proxy for Airtable endpoints.
5. Build target URL: `https://api.airtable.com/v0/{path}`.
6. Build headers including `Authorization: Bearer <AIRTABLE_TOKEN>`.
7. Forward method, URL, query params, and JSON body using `requests.request`.
8. Return Airtable’s response JSON + status code.

This design keeps the proxy **thin and transparent**.

---

## 9. Deployment (Render Free Tier)

This repo includes a `render.yaml` so Render can auto-configure the service.

### 9.1. Required Files

- `app.py`
- `requirements.txt` (includes `gunicorn`)
- `render.yaml`

### 9.2. `render.yaml` (Summary)

```yaml
services:
  - type: web
    name: airtable-proxy
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: AIRTABLE_TOKEN
        sync: false
```

### 9.3. Steps to Deploy

1. Push this repo to GitHub.
2. Go to <https://render.com> → create account / log in.
3. **New +** → **Web Service** → connect your GitHub repo.
4. Render will pick up `render.yaml` automatically.
5. In Render dashboard → service → **Environment**:
   - Add `AIRTABLE_TOKEN` with your real PAT.
6. Click **Deploy** (or wait for auto-deploy on push).

You’ll get a URL like:

```text
https://airtable-proxy.onrender.com
```

You can then call:

```text
https://airtable-proxy.onrender.com/v0/appoPztPp3kjnaI4Q/Books
```

---

## 10. Python Basics for JS/Node Developers (Cheat Sheet)

### Syntax Differences

| Concept        | JavaScript                 | Python                   |
| -------------- | -------------------------- | ------------------------ |
| Indentation    | Optional (`{}`)           | **Required** (4 spaces)  |
| Variables      | `let`, `const`, `var`     | just `x = 5`             |
| Functions      | `function`, `=>`          | `def`                    |
| Null           | `null`                    | `None`                   |
| Boolean        | `true`, `false`          | `True`, `False`          |
| Print          | `console.log()`           | `print()`                |
| Arrays         | `[]`                      | `[]` (lists)             |
| Objects        | `{}`                      | `{}` (dicts)             |
| String format  | `` `Hello ${name}` ``     | `f"Hello {name}"`     |
| Async          | `async/await`             | `async/await`            |
| Imports        | `import` / `require`      | `import` / `from x import y` |
| Package mgr    | `npm`                     | `pip`                    |

### Example: JS vs Python

```javascript
// JavaScript
const greet = (name) => {
  if (name === null) {
    return "Hello, stranger!";
  }
  return `Hello, ${name}!`;
};

const numbers = [1, 2, 3];
numbers.forEach((n) => console.log(n));
```

```python
# Python

def greet(name):
    if name is None:
        return "Hello, stranger!"
    return f"Hello, {name}!"

numbers = [1, 2, 3]
for n in numbers:
    print(n)
```

---

## 11. Useful Resources

### Python

- [Python Official Tutorial](https://docs.python.org/3/tutorial/)
- [Real Python](https://realpython.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)

### Airtable API

- [Airtable API Docs](https://airtable.com/developers/web/api/introduction)
- [Create PAT](https://airtable.com/create/tokens)
- [API Scopes](https://airtable.com/developers/web/api/scopes)

---

## 12. Status

- Local proxy: ✅
- Airtable integration: ✅
- Render deployment config: ✅

You can now safely expose this proxy endpoint to LLMs or other clients without revealing your Airtable token.
