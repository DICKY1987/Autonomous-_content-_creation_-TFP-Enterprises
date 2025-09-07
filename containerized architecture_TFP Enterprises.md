containerized architecture_TFP Enterprises
This document provides a comprehensive set of instructions for an agentic AI to migrate the Autonomous Content Creation – TFP Enterprises system from its current monolithic codebase into a modular, containerized architecture. The plan is divided into three phases—Decomposition, Modularization and Containerization—with clear deliverables, acceptance criteria and guardrails. The goal is to maintain functional parity while improving scalability, maintainability and reliability.
The existing project documentation describes a complex platform for automated content creation. Core services include a content research engine, asset generation pipeline, voice synthesis service, video assembly module, quality assurance gate and multi‑platform distribution service[1]. The project structure comprises a large src directory with submodules for research, quality, business logic and specialized tools, along with scripts for uploading and rendering[2]. A business plan further defines the desired architecture as an event‑driven system orchestrated by a central controller, with discrete services for topic intake, research, script generation, asset processing, text‑to‑speech (TTS), video assembly, QA/compliance, metadata optimization, uploaders and analytics[3]. The data plane consists of S3 storage, Postgres and Redis, while the control plane relies on Celery workers coordinated by a FastAPI orchestrator[4]. Current documentation also recommends merging duplicated content systems into a single content_system package with submodules like research, script, assets, tts, assembly, qa, metadata, uploaders, platform_specs, analytics, experiments and orchestrator[5], and provides a unified repository layout with an infra directory for infrastructure manifests[6].
The instructions below are tailored to this context and assume the AI has access to the existing code and documentation. They should be followed sequentially, starting with architectural decomposition, moving through code reorganization, and concluding with container packaging and deployment.
Definitions
•	Monolith – The current repository containing all logic, scripts and assets in one interdependent codebase.
•	Module / Service – A cohesive unit of functionality with a clear API and data contract. In this plan each core capability (e.g., research, script generation) becomes its own service.
•	Container – A self‑contained runtime image (Docker) encapsulating code, dependencies and configuration. Containers ensure portability and consistent execution across environments.
•	Event – An asynchronous message (published on Redis/NATS) carrying a payload conforming to a versioned JSON Schema (e.g., PriceTick@1.0, IndicatorVector@1.1 in the trading example). This plan defines events like ResearchRequest@1.0 and ScriptDraft@1.0 for the content system.
Phase 1 – Decomposition (Architecture & Contracts)
Objectives
1.	Identify domain boundaries and split the monolith into services. The business plan describes distinct capabilities such as topic research, script generation, asset pipeline, TTS, video assembly, QA/compliance, metadata optimization, uploaders and analytics[3]. Each of these will become an independent service.
2.	Define the data and control planes. Use S3 (object storage), Postgres (relational database) and Redis (cache/pub‑sub) as the data plane[4]. Use Celery workers coordinated by a FastAPI orchestrator as the control plane to run asynchronous tasks and orchestrate workflows[4].
3.	Specify interfaces and contracts. For each service, define synchronous HTTP/gRPC APIs and asynchronous event messages with versioned JSON Schemas. Adopt OpenAPI 3.0 for HTTP specifications and JSON Schema for event definitions.
Deliverables
1.	Service Catalog (docs/modernization/01_service_catalog.md). Document each service with its purpose, inputs, outputs, dependencies, expected scale and service‑level objectives. Use the list of modules from the business plan as a starting point[3]. Example entries:
Service	Purpose	Inputs	Outputs
topic‑research	Accept a topic and perform online research to produce factual and trending data.	ResearchRequest@1.0 (event)	ResearchData@1.0 (event)
script‑generator	Turn research data into a compelling script.	ResearchData@1.0 (event)	ScriptDraft@1.0 (event)
asset‑pipeline	Generate images, graphics and B‑roll; fetch from stock libraries.	ScriptDraft@1.0 (event), optional direct API calls to stock providers	AssetPackage@1.0 (event)
tts‑service	Convert the script into voice over segments.	ScriptDraft@1.0 (event)	AudioClip@1.0 (event)
video‑assembly	Combine assets, audio and video snippets into the final video using FFmpeg/MoviePy (see existing SOP)[7].
AssetPackage@1.0, AudioClip@1.0	VideoFile@1.0 (event)
qa‑compliance	Run quality checks and compliance gates on the final video.	VideoFile@1.0	ApprovedVideo@1.0 (event) or RejectionReport@1.0
metadata‑optimizer	Generate titles, descriptions, tags and thumbnails.	ApprovedVideo@1.0	Metadata@1.0 (event)
uploader‑gateway	Upload the video and metadata to YouTube, TikTok and other platforms using platform‑specific rules[3].
ApprovedVideo@1.0, Metadata@1.0	UploadReport@1.0 (event)
analytics‑collector	Track performance metrics, viewer engagement and feedback loops for continuous improvement[3].
Various platform callbacks	AnalyticsRecord@1.0 (event)
orchestrator	Central coordinator that listens for events and schedules tasks via Celery workers[4].
all events	orchestrates workflows
1.	Boundaries & Events Document (docs/modernization/02_boundaries_and_events.md). Provide high‑level diagrams (e.g., Mermaid or PlantUML) illustrating service boundaries, data flows and event channels. Use the event‑driven flow described in the business plan (from POST /topics through research, script, assets, TTS, assembly, QA, metadata and uploaders)[8]. Specify which interactions are synchronous (HTTP/gRPC) and which are asynchronous (events through Redis/NATS). Example:
flowchart LR
  T[Topic Intake] -- ResearchRequest@1.0 --> R[topic‑research]
  R -- ResearchData@1.0 --> S[script‑generator]
  S -- ScriptDraft@1.0 --> A[asset‑pipeline]
  S -- ScriptDraft@1.0 --> V[tts‑service]
  A -- AssetPackage@1.0 --> C[video‑assembly]
  V -- AudioClip@1.0 --> C
  C -- VideoFile@1.0 --> Q[qa‑compliance]
  Q -- ApprovedVideo@1.0 --> M[metadata‑optimizer]
  M -- Metadata@1.0 --> U[uploader‑gateway]
  U -- UploadReport@1.0 --> O[analytics‑collector]
  R & S & A & V & C & Q & M & U --> O
1.	Contracts Directory (contracts/). Create subdirectories:
2.	openapi/: YAML files specifying HTTP APIs for synchronous calls (e.g., orchestrator endpoints, analytics retrieval). Include sample specs for endpoints such as /topics (submit a topic), /report (fetch analytics). Use OpenAPI 3.0.
3.	events/: JSON Schema definitions for each event (e.g., ResearchRequest@1.0.json, ScriptDraft@1.0.json, VideoFile@1.0.json). Each schema must define type, required fields, allowed values and any nested structures. Version numbers must be embedded in the schema IDs.
4.	schemas/: Shared domain entities (e.g., Topic@1.0, VideoMetadata@1.0) used across multiple events.
5.	Architecture Decision Record (ADR) (docs/adr/ADR-0001-service-decomposition.md). Explain the rationale for splitting the monolith into services based on the distinct capabilities identified[3]. Document alternatives considered (e.g., staying monolithic or only partially splitting), reasons for choosing event‑driven micro‑services, and potential risks (e.g., increased deployment complexity). Provide mitigation strategies such as using asynchronous queues, schema versioning and backward compatibility.
Acceptance Criteria
1.	No orphan capabilities. Every major function described in the business plan is mapped to exactly one service. The service catalog is exhaustive.
2.	Versioned contracts. Each event and API definition includes an explicit version (e.g., @1.0). JSON Schemas and OpenAPI files validate successfully with linter tools.
3.	Diagram completeness. The boundaries document shows all data flows from topic intake through upload and analytics. All event channels and synchronous calls are labeled.
Guidance and Assumptions
•	Use the existing docs/AI_Youtube_BusinessPlan_Hierarchical.md for the high‑level workflow, data plane and control plane definitions[3][4].
•	Incorporate the existing SOP for video assembly and uploading (e.g., FFmpeg commands, file naming conventions) into the video‑assembly and uploader services as part of the service description[7].
•	Keep event payloads small and focused; use IDs to reference large artefacts stored in S3.
•	Guarantee idempotency for tasks that have external side effects (e.g., uploading to YouTube, generating assets) by including unique run IDs or checksums in requests.
Phase 2 – Modularization (Code Restructuring)
Objectives
1.	Reorganize the codebase into service‑oriented modules. Create a content_system/ package containing submodules for each service (research, script, assets, tts, assembly, qa, metadata, uploaders, platform specs, analytics, experiments, orchestrator) as suggested in the business plan[5]. Move related functions, models and adapters into these modules.
2.	Define internal boundaries. Within each service module, separate core logic (pure functions and domain classes) from side‑effectful adapters (e.g., HTTP calls to stock providers, database access, S3 uploads). Expose a clean public API for the module.
3.	Introduce contract tests. For each service, write unit tests to validate that outgoing events adhere to the JSON Schemas and that HTTP endpoints conform to OpenAPI definitions. Add end‑to‑end tests to ensure the orchestrator can run a complete pipeline using mocks for external services.
4.	Update build and CI. Configure the Python workspace (e.g., Poetry or Pipenv) or Node workspace to handle multiple packages. Create a top‑level pyproject.toml with sub‑package declarations, or a multi‑module setup for other languages. Set up a GitHub Actions workflow to run unit tests, contract validation and linting on each commit.
Deliverables
1.	Module Layout Document (docs/modernization/03_module_layout.md). Describe the directory structure of the reorganized codebase. For example:
content_system/
  research/
    core/
    adapters/
    tasks.py
    __init__.py
  script/
    core/
    adapters/
    tasks.py
  assets/
    core/
    adapters/
    tasks.py
  ...
infra/
  docker-compose.yml
  k8s/
    research-deployment.yaml
    script-deployment.yaml
    ...
scripts/
  dev-up.sh
tests/
  contracts/
  e2e/
... (other files)
1.	Source Modules. Under content_system/ create sub-packages for each service. Each module should include:
2.	core/ – pure logic, dataclasses/pydantic models, domain functions.
3.	adapters/ – integrations with external systems (HTTP clients, database connectors, file operations). The adapter layer should implement idempotent operations with retry logic.
4.	tasks.py – Celery tasks or asynchronous handlers that call core functions and publish events.
5.	__init__.py to expose public APIs (e.g., research.process(topic_id: str) -> ResearchData).
6.	Tests. Under tests/, add:
7.	unit/ for core logic tests.
8.	contracts/ for validating event schemas and HTTP APIs.
9.	e2e/ for end‑to‑end flows using mocks for external dependencies.
10.	Build Configuration. Update or create pyproject.toml (if Python) or equivalent to define multiple packages. Set up scripts/dev-up.sh to run docker compose up and start the full stack in development.
11.	CI Pipeline (.github/workflows/ci.yml). Add a GitHub Actions workflow that installs dependencies, runs linting and tests, and validates OpenAPI and JSON Schema files. Fail the build if any contract test fails.
Acceptance Criteria
1.	Each module builds independently. Running pytest services/research (or the equivalent) executes its unit and contract tests without errors.
2.	No cross‑module imports of core logic. Modules communicate exclusively through defined event schemas or interfaces. Shared utilities live in a content_system/common package.
3.	Adapters are thin and replaceable. All external side effects (HTTP calls, file I/O) occur only in adapter classes. Core logic is pure and testable.
4.	CI is green. All tests pass and the schema validation steps succeed on every push.
Guidance and Assumptions
•	Follow the unified repository layout recommended in the business plan[6]. Place infrastructure manifests in an infra/ directory and keep service code under content_system/.
•	Use Pydantic or dataclasses for data models; they can generate JSON Schemas automatically.
•	Use Celery for asynchronous tasks; each service’s tasks.py should define Celery tasks that call core functions and publish events to Redis.
•	Use asynchronous HTTP clients (e.g., httpx) and unify error handling and retry logic in adapter classes.
Phase 3 – Containerization (Runtime & Ops)
Objectives
1.	Package each service into a Docker image. Each module’s tasks.py and related code should be runnable in an isolated container. The image must install only necessary dependencies, use a non‑root user, and define a health check.
2.	Compose the system for local development. Provide a docker-compose.yml under infra/ that starts all services, along with Redis, Postgres and MinIO (S3 compatible object storage). Define named volumes for data persistence and environment variables for configuration.
3.	Define Kubernetes manifests for production. Under infra/k8s/, add deployment.yaml, service.yaml and optional HorizontalPodAutoscaler.yaml for each service. Provide a namespace.yaml and configmap.yaml for configuration and secrets. Use liveness/readiness probes and resource requests/limits.
4.	Add observability and logging. Ensure each container logs structured JSON to STDOUT. Set up health endpoints /healthz and readiness endpoints /ready. Plan integration with a centralized logging and metrics stack (e.g., Prometheus, Grafana, Loki) but actual integration can be a future phase.
Deliverables
1.	Dockerfiles (services/<name>/Dockerfile). For each service, write a Dockerfile that:
2.	Starts from a minimal base (e.g., python:3.11-slim).
3.	Copies only that service’s code and dependencies.
4.	Installs dependencies (poetry/pipenv or pip) with pinned versions.
5.	Creates a non‑root user and switches to it.
6.	Defines environment variables via a .env file or argument.
7.	Exposes the port used by the service (if any) and sets a HEALTHCHECK command (curl to /healthz).
8.	Docker Compose File (infra/docker-compose.yml). Include:
9.	redis: the broker and pub/sub system.
10.	postgres: the relational database.
11.	minio: an S3 compatible storage service (or use Amazon S3 in production).
12.	A container for each service (research, script, assets, tts, assembly, qa, metadata, uploaders, analytics, orchestrator). Each should reference its Dockerfile and mount volumes when necessary.
13.	Environment variables and networks configured so services can discover one another. Use depends_on to enforce startup order.
14.	Kubernetes Manifests. For each service:
15.	deployment.yaml with appropriate replicas, resource requests (CPU/memory) and container spec.
16.	service.yaml to expose the service inside the cluster (ClusterIP) or externally (if needed).
17.	configmap.yaml and secret.yaml for configuration and sensitive values (API keys, DB credentials).
18.	Optionally a HorizontalPodAutoscaler.yaml to scale tasks based on CPU or custom metrics.
19.	Runbooks (docs/runbooks/<service>_runbook.md). Document how to deploy, monitor and troubleshoot each service. Include steps to restart failed tasks, view logs, update environment variables and perform rollbacks.
Acceptance Criteria
1.	Local environment boots successfully. Running docker-compose up starts all services, and health endpoints return 200. The orchestrator can accept a topic and trigger the end‑to‑end pipeline.
2.	Images follow best practices. Each image runs as a non‑root user, uses a minimal base, has a defined entrypoint, a health check, and a pinned dependency lock file. Image vulnerability scanning (Trivy or similar) shows no critical vulnerabilities.
3.	Kubernetes manifests deploy. Applying the manifests to a cluster (kind, k3s or minikube) brings up the system successfully. Pods have readiness and liveness probes configured and the orchestrator can execute workflows across the cluster.
4.	Observability hooks exist. Each service logs in structured JSON, exposes health endpoints, and uses environment variables for configuration. The runbooks describe how to integrate with central logging and metrics.
Guidance and Assumptions
•	Use the unified repository layout recommended in the business plan[6]. Place Dockerfiles under each service and infrastructure manifests under infra/.
•	Use environment variables for configuration; provide .env.example files for local use. Use Kubernetes secrets for sensitive keys in production.
•	For the orchestrator container, include the FastAPI app and Celery worker; run them as separate processes using a process manager (e.g., supervisord) or separate deployments.
•	For media processing (FFmpeg, MoviePy), install only necessary binaries in the video‑assembly container; avoid bundling heavy dependencies into other service images.
Guardrails & Conventions
To ensure reliability and maintainability throughout the migration, apply the following conventions in all phases:
1.	Idempotency & Retries. Tasks that perform external side effects (e.g., uploading a video or creating an asset) must be idempotent. Use unique identifiers to detect duplicates and safe retry logic with exponential backoff.
2.	Schema Versioning. All events and APIs must specify versions (@1.0, @1.1, etc.). Maintain backward compatibility by evolving schemas with additive changes or by supporting multiple versions simultaneously.
3.	Separation of Concerns. Keep core logic (pure functions) separate from adapters and tasks. Avoid cross‑module imports of core logic to prevent tight coupling.
4.	Observability. Log structured JSON with correlation IDs (trace IDs). Expose health and readiness endpoints for orchestrators and services. Use metrics to measure throughput, latency and error rates.
5.	Infrastructure as Code. Store all manifest files (Compose, K8s) in infra/ and version them alongside code. Use environment variables or ConfigMaps for configuration; never hard‑code secrets.
Conclusion
By following this phased plan, the Autonomous Content Creation – TFP Enterprises system can be systematically transformed from a large monolithic repository into a suite of modular, containerized services. The decomposition phase identifies clear boundaries and contracts, the modularization phase restructures code into independent modules with explicit interfaces, and the containerization phase packages and orchestrates those modules for deployment on both local and cluster environments. Applying these practices will enhance reliability, scalability and maintainability, enabling the platform to adapt and evolve as new content generation capabilities emerge.
________________________________________
[1] [2] CLAUDE.md
https://github.com/DICKY1987/Autonomous-_content-_creation_-TFP-Enterprises/blob/16c488b34098ec0267b3d4cf9c53ca22f369f601/docs/CLAUDE.md
[3] [4] [5] [6] [8] AI_Youtube_BusinessPlan_Hierarchical.md
https://github.com/DICKY1987/Autonomous-_content-_creation_-TFP-Enterprises/blob/16c488b34098ec0267b3d4cf9c53ca22f369f601/docs/AI_Youtube_BusinessPlan_Hierarchical.md
[7] SOP_Sections_3.4_to_3.6.md
https://github.com/DICKY1987/Autonomous-_content-_creation_-TFP-Enterprises/blob/16c488b34098ec0267b3d4cf9c53ca22f369f601/docs/SOP_Sections_3.4_to_3.6.md
