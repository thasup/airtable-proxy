---
description: "Task list for feature implementation"
---

# Tasks: Secure Proxy Server for AI Agents

**Input**: Design documents from `/specs/001-secure-proxy-server/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize Python repository setup with `requirements.txt` containing FastAPI, httpx, uvicorn, pytest.
- [x] T002 [P] Create project structure via `mkdir -p src/core src/db src/routers tests/integration tests/unit`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T003 Create `src/core/config.py` to securely load `AIRTABLE_PAT`, `ADMIN_SECRET`, and `DB_PATH`.
- [x] T004 Initialize SQLite DB and table schema for `AgentToken` and `AccessLog` in `src/db/connection.py`.
- [x] T005 [P] Create base FastAPI application instance in `src/main.py`.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Secure Setup and Local Agent Access (Priority: P1) 🎯 MVP

**Goal**: As a system owner, I want to deploy the proxy server so that my own local AI agents can securely access Airtable data.

**Independent Test**: Can be fully tested by inserting a valid pre-authorized agent token in the database, sending a simulated Airtable request, and verifying it succeeds, while any unauthorized requests fail.

### Implementation for User Story 1

- [x] T006 [P] [US1] Create read queries for token validation (`get_active_token`) in `src/db/tokens.py`.
- [x] T007 [P] [US1] Implement token verification logic mapping to the Airtable proxy in `src/core/security.py`.
- [x] T008 [US1] Implement the wildcard proxy mechanism via `httpx.AsyncClient` in `src/routers/proxy.py`.
- [x] T009 [US1] Include `proxy.py` router inside `src/main.py`.
- [x] T010 [US1] Create proxy endpoint test verifying proxy logic and missing authentication rejection in `tests/integration/test_proxy.py`.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. MVP can run proxying calls manually populated in the DB.

---

## Phase 4: User Story 2 - Authenticate External AI Agents (Priority: P2)

**Goal**: As a system owner, I want to provide a mechanism for other (external) AI agents to authenticate themselves using tokens via an admin API.

**Independent Test**: Can be fully tested by targeting `POST /admin/tokens`, extracting the `sk_agent_` key, and leveraging it against the US1 proxy route successfully.

### Implementation for User Story 2

- [x] T011 [P] [US2] Create write/delete queries (`create_token`, `revoke_token`) in `src/db/tokens.py`.
- [x] T012 [P] [US2] Implement administrative token APIs conforming to `POST /admin/tokens` and `DELETE /admin/tokens/{id}` in `src/routers/admin.py`.
- [x] T013 [US2] Include `admin.py` router inside `src/main.py`.
- [x] T014 [US2] Write tests verifying admin token lifecycle operations in `tests/integration/test_admin.py`.

**Checkpoint**: At this point, both internal proxying and external credential provisioning are operating safely.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T015 [P] Implement `AccessLog` structured logging mechanism in `src/core/logging.py`.
- [x] T016 Setup in-memory rate limiting middleware applying to proxy attempts in `src/main.py`.
- [x] T017 Validate configuration against `quickstart.md` locally via a local run script.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2). Relies on the database setup and token hash checking patterns from US1, but conceptually independent.

### Parallel Opportunities

- Creating folder hierarchies (Setup) can be run concurrently with dependency definitions.
- US1 DB token checks and the token authentication dependencies can be developed locally.
- US2 routing features don't block the wildcard path and can technically be worked on while the async proxying mechanism is being perfected.

### Parallel Example: User Story 1

```bash
# Data Layer
Task: Create read queries for token validation in src/db/tokens.py
# Security Logic
Task: Implement token verification logic in src/core/security.py
```
