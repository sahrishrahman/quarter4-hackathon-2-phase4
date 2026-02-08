<!--
Sync Impact Report:
Version change: 1.0.0 → 2.0.0
Modified principles: All principles completely redefined for Phase II
Added sections: Project Overview, Core Requirements, Authentication & Security, Non-Functional Requirements, Technology Stack and Tools, Development Workflow, Monorepo Structure, Guiding Principles, Deliverables and Success Criteria
Removed sections: Original template placeholders
Templates requiring updates: ✅ Updated
Follow-up TODOs: None
-->

# Full-Stack Web Application for The Evolution of Todo - Phase II Constitution

## Project Overview

This constitution governs the evolution of a single-user console-based todo application to a modern multi-user full-stack web application with persistent storage. The application transitions from an in-memory console app to a secure, authenticated web platform with Neon PostgreSQL persistence, supporting multiple concurrent users with proper data isolation.

The primary focus is on implementing the 5 core task features (Add, Delete, Update, View, Mark Complete) in a web context with robust authentication and user isolation. This document serves as the foundational governance for Phase II, defining high-level goals, requirements, security model, technology stack, monorepo structure, and strict agentic development rules.

## Core Principles

### I. Spec-First Development
All features must be fully specified before implementation begins. Specifications must include user stories, acceptance criteria, API contracts, database schemas, and UI mockups. No implementation work proceeds without approved specifications in the `specs/` directory.

### II. Security by Design
All features must implement user authentication and data isolation from the ground up. Every API endpoint must enforce user ownership validation. No feature is considered complete without proper security measures in place, including JWT-based authentication and user-specific data access controls.

### III. Test-First Implementation (NON-NEGOTIABLE)
All code must be developed following TDD practices: tests written → specifications approved → tests fail → then implement. Both unit and integration tests are required for all features. The application must maintain a minimum 80% code coverage threshold.

### IV. Full-Stack Integration
All features must be implemented with both frontend and backend components working together. Each feature must be testable through both the UI and API layers. No backend-only or frontend-only implementations are acceptable without explicit UI or API specifications.

### V. Agentic Development Compliance
All implementation must be performed exclusively through Claude Code agents and Spec-Kit Plus tools. Manual coding outside of agent guidance is strictly prohibited. All changes must be traceable through Prompt History Records (PHRs).

### VI. API-First Design

All backend functionality must be exposed through well-defined RESTful API endpoints before frontend implementation. API contracts must be documented and versioned appropriately. Frontend development must consume these APIs exclusively.

## Authentication & Security

The application implements JWT-based authentication using Better Auth for the Next.js frontend, with tokens verified by FastAPI middleware on the backend. A shared BETTER_AUTH_SECRET ensures secure token validation across services. All operations enforce user isolation, ensuring users can only access their own data.

Authentication requirements:
- All API endpoints (except authentication endpoints) require valid JWT tokens
- User ID is extracted from JWT and used for data access validation
- All database queries must include user_id filters for proper isolation
- Session management handled through Better Auth with secure token storage

## Non-Functional Requirements

- Code Quality: TypeScript standards for frontend, PEP 8 for backend
- Modularity: Components and services must be loosely coupled and independently testable
- Type Safety: Full TypeScript typing for all frontend code; proper type hints for Python backend
- Responsive UI: Mobile-first design with responsive layouts
- Error Handling: Proper HTTP status codes and user-friendly error messages
- Performance: Page load times under 3 seconds, API response times under 500ms
- Accessibility: WCAG 2.1 AA compliance for core functionality

## Technology Stack and Tools

### Frontend Layer
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Better Auth (with JWT plugin)

### Backend Layer
- Python 3.11+
- FastAPI
- SQLModel
- Neon PostgreSQL
- PyJWT

### Development & Infrastructure
- Claude Code
- Spec-Kit Plus
- Docker Compose
- Git

### Testing & Quality
- Jest (frontend)
- pytest (backend)
- Playwright (e2e)

## Development Workflow

The agentic development stack follows this sequence: constitution → specifications → plans → agents/skills → implementation → testing → iteration. All development must be performed without manual coding, using Claude Code agents exclusively. Each step must be documented with Prompt History Records.

1. Create detailed specifications in `specs/` directory
2. Generate implementation plans using `/sp.plan`
3. Execute implementation via agent tasks using `/sp.implement`
4. Test and validate functionality
5. Iterate based on feedback

## Monorepo Structure

```
NewFullstack/
├── .specify/
│   ├── memory/constitution.md
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   └── tasks-template.md
│   └── config.yaml
├── specs/
│   ├── features/
│   │   ├── auth/
│   │   └── todo/
│   ├── api/
│   ├── database/
│   └── ui/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
├── backend/
│   ├── app/
│   ├── models/
│   ├── api/
│   └── tests/
├── .claude/
│   └── agents/
├── .specify/
│   └── memory/
├── history/
│   ├── prompts/
│   └── adr/
├── docker-compose.yml
├── CLAUDE.md
└── README.md
```

## Guiding Principles

- Spec-first development: All features must be fully specified before implementation
- Security by design: User isolation and authentication implemented from the start
- Simplicity: Start with minimal viable implementation, add complexity only when necessary
- Maintainability: Code must be readable, documented, and easily modifiable
- Preparation for Phase III: Architecture must support future chatbot integration
- Full process transparency: All development steps documented for hackathon evaluation

## Deliverables and Success Criteria

- Working full-stack application deployable via docker-compose
- All core features functional through both responsive UI and REST API
- Secure multi-user isolation with proper authentication
- Clean, agent-generated code with comprehensive documentation
- Complete specifications history in `specs/` directory
- Demo-ready application with sample users and tasks
- All functionality tested with unit, integration, and end-to-end tests

## Governance

This constitution supersedes all other development practices for Phase II. All amendments require explicit documentation, approval, and migration planning. All pull requests and code reviews must verify compliance with these principles. All development must be traceable through Prompt History Records in the `history/prompts/` directory.

**Version**: 2.0 | **Ratified**: 2025-12-30 | **Last Amended**: 2025-12-30
