# Airtable Proxy API Contracts

## 1. Proxy Requests
All requests are routed to the Airtable API under exactly the same path, substituting authentication.

### **Endpoint**: `/*`
Matches all standard Airtable endpoints, including `GET /v0/appBaseId/TableId`, `POST /v0/app...`, `PATCH`, `DELETE`.

- **Headers Needed**:
  - `Authorization: Bearer <AGENT_TOKEN>` (Must be issued by Admin API below)

- **Proxy Behavior Check**:
  - Validates `AGENT_TOKEN` against DB cache/storage.
  - Checks if Token `is_active` is True and `baseId` (extracted from URL path) is permitted in `allowed_bases`.
  - Replaces `Authorization` header with the server's single secured `AIRTABLE_PAT`.
  - Forwards the request securely to `https://api.airtable.com/*`.
  - Returns the exact upstream Airtable response back to the AI Agent client, preserving error codes and bodies transparently.

## 2. Admin API
REST management interface for managing agent access tokens. (Requires an Admin token set via proxy environment variables).

### **Endpoint**: `POST /admin/tokens`
Generates a new token for an AI agent.
- **Headers Needed**:
  - `Authorization: Bearer <SERVER_ADMIN_KEY>`
- **Body**: 
  ```json
  {
    "name": "Local Agent Worker 1",
    "allowed_bases": ["appXYZ123", "appABC789"]
  }
  ```
- **Response**: 
  ```json
  {
    "id": "e4c19...",
    "token": "sk_agent_abc123...",
    "name": "Local Agent Worker 1",
    "allowed_bases": ["appXYZ123", "appABC789"],
    "created_at": "2026-03-11T00:00:00Z",
    "is_active": true
  }
  ```
> **Note**: This is the ONLY time `token` is shown in plain text. It must be saved by the user securely.

### **Endpoint**: `DELETE /admin/tokens/{id}`
Revokes the agent's access token entirely.
- **Headers Needed**:
  - `Authorization: Bearer <SERVER_ADMIN_KEY>`
- **Response**: `200 OK`
