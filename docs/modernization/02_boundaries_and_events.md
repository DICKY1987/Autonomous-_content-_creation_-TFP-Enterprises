# Service Boundaries and Event Flows

The following diagram illustrates the event-driven architecture for the content system. Solid arrows denote asynchronous events transmitted via Redis (or NATS). Synchronous HTTP calls are labeled accordingly.

```mermaid
flowchart LR
  T[Topic Intake]
  T -- ResearchRequest@1.0 --> R[topic-research]
  R -- ResearchData@1.0 --> S[script-generator]
  S -- ScriptDraft@1.0 --> A[asset-pipeline]
  S -- ScriptDraft@1.0 --> V[tts-service]
  A -- AssetPackage@1.0 --> C[video-assembly]
  V -- AudioClip@1.0 --> C
  C -- VideoFile@1.0 --> Q[qa-compliance]
  Q -- ApprovedVideo@1.0 --> M[metadata-optimizer]
  M -- Metadata@1.0 --> U[uploader-gateway]
  U -- UploadReport@1.0 --> O[analytics-collector]
  R & S & A & V & C & Q & M & U --> O
```

All services expose `GET /healthz` for liveness checks. The orchestrator interacts with each service via HTTP for control actions (e.g., `POST /topics`) while publishing and subscribing to the events shown above.
