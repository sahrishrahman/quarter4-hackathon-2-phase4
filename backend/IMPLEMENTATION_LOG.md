# Implementation Log: Todo Backend API

## Phase Completions
- [x] Phase 1: Setup & Dependencies
- [x] Phase 2: Foundational (DB, Security, Routing)
- [x] Phase 3: User Story 1 (Secure CRUD)
- [x] Phase 4: User Story 2 (Filtering)
- [x] Phase 5: User Story 3 (Feedback & Performance)
- [x] Phase 6: Polish & Security Audit

## Security Audit Decisions
- Used `pyjwt` with HS256 for signature verification.
- Implemented `get_current_user` dependency that validates `sub` claim.
- Every task route validates `user_id` in path against `current_user` in JWT.
- SQLModel queries always filtered by `user_id`.
