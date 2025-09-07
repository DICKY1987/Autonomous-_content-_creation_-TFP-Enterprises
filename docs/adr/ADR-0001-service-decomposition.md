# ADR-0001: Service Decomposition

## Status
Accepted

## Context
The original repository is a monolithic codebase that couples topic research, script generation, media processing and distribution logic. Scaling individual capabilities independently is difficult and deploys require full‑repo coordination.

## Decision
Split the monolith into discrete services: topic-research, script-generator, asset-pipeline, tts-service, video-assembly, qa-compliance, metadata-optimizer, uploader-gateway, analytics-collector and a central orchestrator. Services communicate via versioned JSON events on Redis and expose minimal HTTP APIs for control.

## Alternatives
- **Remain monolithic:** simpler deployment but poor scalability and high coupling.
- **Partial modularization:** only extract heavy tasks (e.g., video-assembly) which leaves cross‑cutting concerns entangled.

## Consequences
- Enables independent scaling and deployment of services.
- Introduces operational complexity; mitigated via docker-compose for local dev and Kubernetes manifests for production.
- Requires robust contract management and schema versioning.
