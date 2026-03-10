# Technical Research & Decisions

## Authentication Mechanism
- **Decision**: Bearer Tokens (Custom API Keys).
- **Rationale**: The constitution requires a "specific technical mechanism (e.g., custom API keys, signed requests)". Bearer tokens are standard, ubiquitous, and natively supported by most AI agent frameworks and HTTP clients (`Authorization: Bearer <token>`). Signed requests add unnecessary complexity for simple agents to implement.
- **Alternatives considered**: HMAC signed requests (rejected due to client-side complexity), mTLS (too operationally complex for lightweight deployments).

## Web Framework
- **Decision**: FastAPI with `httpx` for async requests, served via `uvicorn`.
- **Rationale**: The success criteria mandates 500 concurrent requests without degradation and <50ms proxy overhead. Asynchronous proxying using FastAPI + `httpx` easily meets these high concurrency and low latency requirements. While Flask is mentioned in the constitution as an example, FastAPI is equally lightweight but offers far superior concurrency performance required by the spec.
- **Alternatives considered**: Flask + `requests` (synchronous nature makes it harder to scale to 500 concurrent connections efficiently without numerous worker processes).

## Credential & Token Storage
- **Decision**: SQLite.
- **Rationale**: Meets FR-003 to "generate, manage, and revoke authentication tokens". SQLite requires zero external dependencies (built into standard Python), minimizing attack surface and operations overhead, while providing ACID properties for secure token management and immediate revocation (SC-004).
- **Alternatives considered**: Environment variables (no dynamic revocation without restarts), Redis (violates the constitution's "minimal dependencies" principle).

## Rate Limiting (Brute-force protection)
- **Decision**: In-memory rate limiting (e.g., using `slowapi` or a custom token bucket in memory).
- **Rationale**: Fulfills the edge case requirement to gracefully block rapid brute-force requests from the public internet. In-memory minimizes dependencies.
- **Alternatives considered**: Redis-based rate limiting (rejected due to added external dependency).
