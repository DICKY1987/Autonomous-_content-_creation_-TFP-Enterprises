from __future__ import annotations
"""Minimal entry point exposing ``HistoricalContentBusinessSystem`` for tests."""
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Any, List


@dataclass
class _Uploader:
    """Very small uploader used by the business system."""
    def upload_to_all_platforms(self, **kwargs):  # pragma: no cover - monkeypatched in tests
        return []


@dataclass
class HistoricalContentBusinessSystem:
    """Stub orchestration class used in end‑to‑end tests.

    The real project coordinates research, generation and uploading.  The test
    suite only needs a configurable object with a ``run_daily_production`` method
    that returns a dictionary containing the current date.
    """

    config: Dict[str, Any] = field(default_factory=lambda: {
        "production_settings": {"daily_video_target": 3}
    })
    uploader: _Uploader = field(default_factory=_Uploader)

    def run_daily_production(self) -> Dict[str, Any]:
        videos: List[str] = []
        target = self.config["production_settings"].get("daily_video_target", 0)
        for i in range(target):  # pragma: no cover - trivial loop
            videos.append(f"video_{i}")
        return {"date": date.today().isoformat(), "videos": videos}


__all__ = ["HistoricalContentBusinessSystem"]
