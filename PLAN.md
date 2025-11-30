# Airtable API Proxy Server - Project Plan

A simple Python proxy server that forwards requests to the Airtable API with proper authentication.

---

## 1. Project Overview

### Goal
Create a proxy server that:
- Receives API requests from LLM or any client
- Attaches the Airtable authentication header (`Authorization: Bearer <PAT>`)
- Forwards the request to `https://api.airtable.com/v0/...`
- Returns the response to the client

### Why a Proxy?
- **Security**: Keep your Airtable Personal Access Token (PAT) server-side
- **Simplicity**: LLM/clients don't need to handle authentication
- **Flexibility**: Add rate limiting, logging, or transformations later

---

## 2. Airtable API Quick Reference

### Base URL
```
https://api.airtable.com/v0/
```

### Authentication
All requests require a Bearer token in the `Authorization` header:
```
Authorization: Bearer YOUR_PERSONAL_ACCESS_TOKEN
```

### Common Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v0/{baseId}/{tableName}` | List records |
| GET | `/v0/{baseId}/{tableName}/{recordId}` | Get a record |
| POST | `/v0/{baseId}/{tableName}` | Create records |
| PATCH | `/v0/{baseId}/{tableName}` | Update records |
| DELETE | `/v0/{baseId}/{tableName}` | Delete records |

### Getting Your PAT
1. Go to https://airtable.com/create/tokens
2. Click "Create token"
3. Add scopes (e.g., `data.records:read`, `data.records:write`)
4. Add bases you want to access
5. Copy the token (shown only once!)

---

## 3. Python Basics for JS/Node Developers

### Key Differences: Python vs JavaScript

| Concept | JavaScript | Python |
|---------|------------|--------|
| **Indentation** | Optional (braces `{}`) | **Required** (4 spaces) |
| **Variables** | `let`, `const`, `var` | Just assign: `x = 5` |
| **Functions** | `function` or `=>` | `def` keyword |
| **Null** | `null` | `None` |
| **Boolean** | `true`, `false` | `True`, `False` |
| **Print** | `console.log()` | `print()` |
| **Arrays** | `[]` | `[]` (called lists) |
| **Objects** | `{}` | `{}` (called dicts) |
| **String format** | `` `Hello ${name}` `` | `f"Hello {name}"` |
| **Async** | `async/await` | `async/await` (similar!) |
| **Import** | `import/require` | `import` / `from x import y` |
| **Package manager** | `npm` | `pip` |

### Quick Syntax Comparison

```javascript
// JavaScript
const greet = (name) => {
    if (name === null) {
        return "Hello, stranger!";
    }
    return `Hello, ${name}!`;
};

const numbers = [1, 2, 3];
numbers.forEach(n => console.log(n));
```

```python
# Python equivalent
def greet(name):
    if name is None:
        return "Hello, stranger!"
    return f"Hello, {name}!"

numbers = [1, 2, 3]
for n in numbers:
    print(n)
```

### Virtual Environments (like node_modules but different)
```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate

# Install packages
pip install flask requests

# Save dependencies
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt
```

---

## 4. Technology Stack

| Component | Choice | Why |
|-----------|--------|-----|
| **Web Framework** | Flask | Simple, beginner-friendly, minimal boilerplate |
| **HTTP Client** | `requests` | Most popular, intuitive API |
| **Config** | `python-dotenv` | Load `.env` files (like dotenv in Node) |
| **WSGI Server** | Built-in (dev) / Gunicorn (prod) | Flask's dev server is fine for learning |

### Alternative: FastAPI
FastAPI is more modern (async, auto-docs) but Flask is simpler for learning.

---

## 5. Project Structure

```
airtable-proxy/
├── app.py              # Main Flask application
├── requirements.txt    # Dependencies (like package.json)
├── .env               # Environment variables (API token)
├── .env.example       # Example env file (safe to commit)
├── .gitignore         # Ignore .env, venv, __pycache__
└── README.md          # Project documentation
```

---

## 6. Implementation Steps

### Step 1: Setup Project
- [ ] Create virtual environment
- [ ] Install dependencies (Flask, requests, python-dotenv)
- [ ] Create `.env` file with Airtable token
- [ ] Create `.gitignore`

### Step 2: Create Basic Flask App
- [ ] Initialize Flask app
- [ ] Create a health check endpoint (`GET /`)
- [ ] Test the server runs

### Step 3: Implement Proxy Logic
- [ ] Create catch-all route for `/v0/*`
- [ ] Extract path and query parameters
- [ ] Forward request to Airtable API with auth header
- [ ] Pass through request body for POST/PATCH
- [ ] Return Airtable response to client

### Step 4: Error Handling
- [ ] Handle missing token
- [ ] Handle Airtable API errors
- [ ] Add basic logging

### Step 5: Testing
- [ ] Test GET request (list records)
- [ ] Test POST request (create record)
- [ ] Test error scenarios

---

## 7. Key Code Concepts to Learn

### Flask Basics
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def hello():
    return {"message": "Hello World"}

if __name__ == "__main__":
    app.run(debug=True)
```

### Environment Variables
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file
token = os.getenv("AIRTABLE_TOKEN")
```

### Making HTTP Requests
```python
import requests

response = requests.get(
    "https://api.airtable.com/v0/baseId/tableName",
    headers={"Authorization": f"Bearer {token}"}
)
data = response.json()
```

### Forwarding Requests (Proxy Pattern)
```python
@app.route("/v0/<path:path>", methods=["GET", "POST", "PATCH", "DELETE"])
def proxy(path):
    # Build target URL
    url = f"https://api.airtable.com/v0/{path}"
    
    # Forward the request
    resp = requests.request(
        method=request.method,
        url=url,
        headers={"Authorization": f"Bearer {token}"},
        params=request.args,
        json=request.get_json(silent=True)
    )
    
    return resp.json(), resp.status_code
```

---

## 8. Security Considerations

- **Never commit `.env`** - Contains your secret token
- **Use HTTPS in production** - Encrypt traffic
- **Consider rate limiting** - Prevent abuse
- **Validate input** - Don't blindly forward everything
- **CORS** - Configure if accessed from browser

---

## 9. Next Steps After Basic Implementation

1. **Add CORS support** - `flask-cors` package
2. **Add logging** - Track requests for debugging
3. **Add rate limiting** - `flask-limiter` package
4. **Docker** - Containerize for easy deployment
5. **Tests** - Add unit tests with `pytest`

---

## 10. Useful Resources

### Python
- [Python Official Tutorial](https://docs.python.org/3/tutorial/)
- [Real Python](https://realpython.com/) - Great tutorials
- [Flask Documentation](https://flask.palletsprojects.com/)

### Airtable API
- [Airtable API Docs](https://airtable.com/developers/web/api/introduction)
- [Create PAT](https://airtable.com/create/tokens)
- [API Scopes](https://airtable.com/developers/web/api/scopes)

---

## Ready to Start?

Run these commands to begin:

```bash
# Navigate to project
cd airtable-proxy

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install flask requests python-dotenv

# Create requirements.txt
pip freeze > requirements.txt
```

Then create your `.env` file:
```
AIRTABLE_TOKEN=pat.xxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxx
```

Let me know when you're ready to implement each step!
