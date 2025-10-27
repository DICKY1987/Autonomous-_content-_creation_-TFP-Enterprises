# Service Boundaries and Events

The diagram below illustrates service boundaries, data flows and event channels in the content system.

```mermaid
flowchart LR
  T[Topic Intake] -- ResearchRequest@1.0 --> R[topic-research]
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

Interactions between services use asynchronous events over Redis/NATS. Synchronous interactions, such as topic submission or analytics retrieval, are exposed via HTTP APIs defined with OpenAPI.

