# Data Model

## Entities

### `AgentToken`
Represents an AI agent that is authorized to use the proxy server.

- **`id`** (UUID, Primary Key): Unique identifier for the agent or standard credential.
- **`name`** (String): Human-readable name of the agent or service, used for logging and auditing.
- **`token_hash`** (String): A SHA-256 hash of the generated API token (sk_agent_...). The raw token is returned to the client only once upon creation, ensuring security.
- **`is_active`** (Boolean): Status of the token. If false, instantly revokes the agent's access.
- **`allowed_bases`** (String / JSON array): A strict list of Airtable base IDs this agent can access, or `["*"]` for global access. Restricts access scopes per agent.
- **`created_at`** (DateTime): Timestamp of when the credential was created.

### `AccessLog`
Optional, but recommended for security auditing (FR-004). Can be implemented via structured text logs or in the DB.
- **`timestamp`** (DateTime): When the attempt occurred.
- **`agent_id`** (UUID, Optional): Present if authentication succeeds.
- **`ip_address`** (String): Source of the request for tracking brute-force attempts.
- **`status_code`** (Integer): Proxy response code returned.
- **`path`** (String): Requested Airtable endpoint path.

## State Transitions
- **Credential Generation**: A new record is inserted as `Active`. The cleartext token is returned to the admin, while only the hash is persisted stringently.
- **Credential Revocation**: A specific `AgentToken` record has `is_active` set to `False`. The check is immediate for all subsequent proxy requests from that token hash as queried by SQLite.
