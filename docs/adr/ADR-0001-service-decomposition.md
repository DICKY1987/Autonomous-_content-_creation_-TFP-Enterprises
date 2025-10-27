# ADR-0001: Service Decomposition

## Status
Accepted

## Context
The existing system is a monolithic repository that bundles research, scripting, asset generation, TTS, video assembly, quality assurance, metadata optimization, uploading and analytics into a single codebase. This coupling makes it difficult to scale individual capabilities or deploy updates independently.

## Decision
Split the monolith into discrete services corresponding to each major capability. Services communicate via versioned events over Redis/NATS and expose HTTP APIs defined with OpenAPI. A FastAPI orchestrator coordinates workflows and schedules Celery tasks.

## Alternatives Considered
- **Remain monolithic:** simpler deployment but poor scalability and high coupling.
- **Partial modularization:** extract only heavy components, leaving others coupled; would still hinder independent deployments.

## Consequences
- **Pros:** improved scalability, clearer ownership boundaries, ability to deploy and scale services independently.
- **Cons:** increased operational complexity; requires schema versioning and robust observability.

## Mitigations
- Use asynchronous queues and idempotent tasks to handle retries safely.
- Version all schemas and maintain backward compatibility.
- Centralize logging and metrics for troubleshooting.

