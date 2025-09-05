from __future__ import annotations
"""Entry point exposing ``HistoricalContentBusinessSystem`` for tests."""
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Any, List

from src.core.automated_content_system import AutomatedContentSystem, ContentConfig
from src.platforms.upload_system import MultiPlatformUploader


@dataclass
class HistoricalContentBusinessSystem:
    """Light‑weight orchestrator used in tests.

    The implementation coordinates the simplified ``AutomatedContentSystem`` and
    ``MultiPlatformUploader`` modules so that integration tests exercise a real
    production flow without hitting external services.
    """

    config: Dict[str, Any] = field(
        default_factory=lambda: {
            "production_settings": {"daily_video_target": 1},
            "topics": ["History"],
        }
    )
    uploader: MultiPlatformUploader = field(default_factory=MultiPlatformUploader)

    def run_daily_production(self) -> Dict[str, Any]:
        target = self.config["production_settings"].get("daily_video_target", 0)
        topics = self.config.get("topics", [])
        videos: List[str] = []

        for topic in topics[:target]:
            system = AutomatedContentSystem(ContentConfig(topic=topic))
            ok, result = system.create_content(topic)
            if ok:
                videos.append(result["output_path"])
                # Upload is stubbed in tests and monkeypatched to avoid side effects
                self.uploader.upload_to_all_platforms(
                    video_path=result["output_path"],
                    topic=topic,
                    content_data=result["content_data"],
                    script=result["script"],
                    image_paths=[],
                    output_dir=".",
                )

        return {"date": date.today().isoformat(), "videos": videos}


__all__ = ["HistoricalContentBusinessSystem"]
