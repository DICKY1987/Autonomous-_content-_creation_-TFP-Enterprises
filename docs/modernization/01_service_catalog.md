# Service Catalog

This document enumerates the services that compose the modularized Autonomous Content Creation platform. Each service maps to a single capability from the business plan and exchanges data via versioned events or HTTP APIs.

| Service | Purpose | Inputs | Outputs |
| --- | --- | --- | --- |
| topic-research | Accept a topic and perform online research to produce factual and trending data. | `ResearchRequest@1.0` (event) | `ResearchData@1.0` (event) |
| script-generator | Turn research data into a compelling script. | `ResearchData@1.0` (event) | `ScriptDraft@1.0` (event) |
| asset-pipeline | Generate images, graphics and B-roll; fetch from stock libraries. | `ScriptDraft@1.0` (event) | `AssetPackage@1.0` (event) |
| tts-service | Convert the script into voice over segments. | `ScriptDraft@1.0` (event) | `AudioClip@1.0` (event) |
| video-assembly | Combine assets, audio and video snippets into the final video using FFmpeg/MoviePy. | `AssetPackage@1.0`, `AudioClip@1.0` | `VideoFile@1.0` (event) |
| qa-compliance | Run quality checks and compliance gates on the final video. | `VideoFile@1.0` (event) | `ApprovedVideo@1.0` or `RejectionReport@1.0` (event) |
| metadata-optimizer | Generate titles, descriptions, tags and thumbnails. | `ApprovedVideo@1.0` (event) | `Metadata@1.0` (event) |
| uploader-gateway | Upload the video and metadata to YouTube, TikTok and other platforms using platform-specific rules. | `ApprovedVideo@1.0`, `Metadata@1.0` | `UploadReport@1.0` (event) |
| analytics-collector | Track performance metrics, viewer engagement and feedback loops for continuous improvement. | Various platform callbacks | `AnalyticsRecord@1.0` (event) |
| orchestrator | Central coordinator that listens for events and schedules tasks via Celery workers. | All events | orchestrates workflows |

Each service is expected to expose health and readiness endpoints and to communicate asynchronously through Redis or another event bus.
