# Service Catalog

This catalog enumerates the services extracted from the monolithic system. Each service lists its purpose, inputs, outputs, dependencies, expected scale and service-level objectives.

| Service | Purpose | Inputs | Outputs |
| --- | --- | --- | --- |
| topic-research | Accept a topic and perform online research to produce factual and trending data. | `ResearchRequest@1.0` (event) | `ResearchData@1.0` (event) |
| script-generator | Turn research data into a compelling script. | `ResearchData@1.0` (event) | `ScriptDraft@1.0` (event) |
| asset-pipeline | Generate images, graphics and B-roll; fetch from stock libraries. | `ScriptDraft@1.0` (event); optional API calls to stock providers | `AssetPackage@1.0` (event) |
| tts-service | Convert the script into voice over segments. | `ScriptDraft@1.0` (event) | `AudioClip@1.0` (event) |
| video-assembly | Combine assets and audio into the final video using FFmpeg/MoviePy. | `AssetPackage@1.0`, `AudioClip@1.0` (events) | `VideoFile@1.0` (event) |
| qa-compliance | Run quality checks and compliance gates on the final video. | `VideoFile@1.0` (event) | `ApprovedVideo@1.0` or `RejectionReport@1.0` (events) |
| metadata-optimizer | Generate titles, descriptions, tags and thumbnails. | `ApprovedVideo@1.0` (event) | `Metadata@1.0` (event) |
| uploader-gateway | Upload the video and metadata to platforms like YouTube and TikTok using platform rules. | `ApprovedVideo@1.0`, `Metadata@1.0` (events) | `UploadReport@1.0` (event) |
| analytics-collector | Track performance metrics, viewer engagement and feedback loops for continuous improvement. | Platform callbacks | `AnalyticsRecord@1.0` (event) |
| orchestrator | Central coordinator that listens for events and schedules tasks via Celery workers. | All events | Orchestrates workflows |

