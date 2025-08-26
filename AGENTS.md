# Feedback system

Read the parent workspace guidance and ignored `openspec/changes/refactor-feedback-platform/` context before continuing work. The active roadmap has 180 meaningful commit boundaries; never create empty commits to meet a count. The requested date interval is pending clarification because January 2025 precedes August 2025.

The backend uses FastAPI and SQLAlchemy. The frontend uses React and TypeScript. Keep authorization in backend policy and query scopes. Treat browser capabilities as presentation data. Every private record lookup and aggregate must apply the current user's database role, grants, and reporting relationship.

Keep drafts private to their author, published feedback visible to its recipient, and administration separate from access to feedback content. Record immutable feedback revisions and metadata-only audit events. Use opaque cookie sessions and CSRF checks on authenticated mutations. Do not restore public role selection or legacy JWT routes.

Keep local OpenSpec, databases, secrets, browser artifacts and task reports ignored. Engineering contracts belong in `docs/`; setup commands belong in `Readme.md`. Run backend regression tests, TypeScript checks, frontend build and affected browser journeys. Push and deployment require a user request.
