# Employee feedback platform

The system combines account roles, explicit privileges, record ownership and the current reporting graph. Employees read their published feedback. Managers author feedback for current direct reports. Senior management reads privacy-protected organization summaries and explicitly escalated feedback. Administrators manage accounts without automatically reading feedback content.

Database queries apply visibility before pagination and aggregation. A browser capability changes presentation only. Drafts remain author-private even when organization reading is granted. A former manager loses team access immediately. No account can grant itself privileges through profile editing.

Opaque session tokens are stored only as SHA-256 hashes. Session cookies are HttpOnly; authenticated mutations require a session-bound CSRF header and a trusted Origin. Account security changes revoke sessions. Requests load current account state instead of trusting cached roles.

Feedback records use optimistic version checks. Every publication and published content edit records an immutable revision. Changes clear recipient acknowledgement. Archival retains history. Comments share the feedback audience. Escalation deliberately discloses one published record to senior management.

SQLite provides durable local storage; PostgreSQL is supported through SQLAlchemy. Alembic owns schema creation. Domain mutations, audit metadata and notifications share a transaction. Audit records contain identifiers and actions rather than employee narrative, tokens or passwords. Organization aggregates require a cohort of at least three employees and never include unpublished drafts.
