"""
Airtable API Proxy Server

A simple proxy that forwards requests to Airtable API with authentication.
"""

import os

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configuration
AIRTABLE_API_BASE = "https://api.airtable.com"
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")


@app.route("/")
def health_check():
    """Health check endpoint - verify the server is running."""
    return jsonify(
        {
            "status": "ok",
            "message": "Airtable Proxy Server is running",
            "token_configured": AIRTABLE_TOKEN is not None,
        }
    )


@app.route("/v0/<path:path>", methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
def proxy(path):
    """
    Proxy endpoint - forwards all requests to Airtable API.

    Example:
        GET /v0/appXXXXXX/TableName -> https://api.airtable.com/v0/appXXXXXX/TableName
    """
    # Check if token is configured
    if not AIRTABLE_TOKEN:
        return (
            jsonify(
                {
                    "error": "AIRTABLE_TOKEN not configured",
                    "hint": "Create a .env file with your Airtable Personal Access Token",
                }
            ),
            500,
        )

    # Build the target URL
    target_url = f"{AIRTABLE_API_BASE}/v0/{path}"

    # Prepare headers - forward content-type if present, add auth
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}

    # Forward Content-Type header if present
    if request.content_type:
        headers["Content-Type"] = request.content_type

    # Get request body for POST/PATCH/PUT requests
    body = request.get_json(silent=True)

    # Forward the request to Airtable
    try:
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.args,  # Forward query parameters
            json=body,  # Forward JSON body
        )

        # Return Airtable's response
        # Try to return as JSON, fallback to text
        try:
            return jsonify(response.json()), response.status_code
        except ValueError:
            return response.text, response.status_code

    except requests.RequestException as e:
        return (
            jsonify({"error": "Failed to connect to Airtable API", "details": str(e)}),
            502,
        )


# This runs when you execute: python app.py
if __name__ == "__main__":
    print("=" * 50)
    print("Airtable Proxy Server")
    print("=" * 50)
    print(f"Token configured: {AIRTABLE_TOKEN is not None}")
    print("Starting server on http://localhost:5000")
    print("=" * 50)

    # Run the development server
    # debug=True enables auto-reload on code changes
    app.run(debug=True, host="0.0.0.0", port=5000)
