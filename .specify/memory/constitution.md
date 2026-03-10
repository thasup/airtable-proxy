<!-- Sync Impact Report
Version Change: 1.0.0 (initial specification)
Modified Principles:
  [PRINCIPLE_1_NAME] -> I. High Security & Privacy
  [PRINCIPLE_2_NAME] -> II. AI Agent Exclusive Access
  [PRINCIPLE_3_NAME] -> III. Public Accessibility & Discoverability
  [PRINCIPLE_4_NAME] -> IV. Agent Authentication & Verification
  [PRINCIPLE_5_NAME] -> (Removed)
Added Sections: 
  - (None, repurposing template sections)
Removed Sections:
  - (None)
Templates requiring updates:
  - .specify/templates/plan-template.md (✅ checked)
  - .specify/templates/spec-template.md (✅ checked)
  - .specify/templates/tasks-template.md (✅ checked)
Follow-up TODOs:
  - Add specific authentication mechanism details (e.g. agent API tokens, signed requests) to technical planning.
-->

# Airtable Proxy Server Constitution

## Core Principles

### I. High Security & Privacy
The primary role of the proxy is to rigorously safeguard Airtable data and Personal Access Tokens (PATs). The server MUST retain all Airtable PATs server-side and never leak credentials to the public internet, mitigating the risk of unauthorized use or data exposure. Preserving the privacy of personal data is the top priority.

### II. AI Agent Exclusive Access
The proxy MUST grant exclusive usage strictly to the owner's permitted AI agents. Broad public access or unauthorized automated bots MUST be actively blocked from reaching the underlying Airtable bases. 

### III. Public Accessibility & Discoverability
Despite being secured, the server MUST be deployed on the public internet. This ensures that any user-owned AI agent with internet access and basic searching/crawling abilities can easily discover, connect to, and reliably retrieve Airtable information through the proxy endpoints without requiring complex VPN setups.

### IV. Agent Authentication & Verification
To balance public reachability with exclusive access, the server MUST implement a robust authentication strategy for the incoming AI agents. There MUST be a specific technical mechanism (e.g., custom API keys, signed requests, or specific headers) that strongly and reliably proves the request actually originates from the user's permitted agents.

## Security & Architecture Standards

Techniques like custom agent API tokens, rate-limiting, and request signature validation SHOULD be employed so the proxy can confidently verify the agent's identity. All dependencies (e.g., Flask, requests, python-dotenv, gunicorn) MUST be kept minimal and closely audited to reduce the external attack surface. Any new endpoint MUST guarantee easy retriability for AI agent failures.

## Development Workflow & Quality Gates

Code reviews MUST verify that new features do not compromise the authentication boundary. Any changes to the API structure MUST maintain compatibility with the AI agent's ability to easily reach and retry requests. Robust logging SHOULD be added to track agent authentication success and failures.

## Governance

This Constitution supersedes all other documentation. 
Amendments to these core principles or authentication strategies require formal documentation and an explicit migration plan for existing permitted AI agents. 
All incoming pull requests and new features MUST be validated against these strict security and authentication principles. 
If an authentication mechanism needs to be changed, it must be properly versioned to avoid breaking existing agents. 
Version updates follow semantic versioning (MAJOR for breaking auth/governance changes, MINOR for new principles, PATCH for typos).

**Version**: 1.0.0 | **Ratified**: 2026-03-11 | **Last Amended**: 2026-03-11
