"""Minimal execution harness for end-to-end tests.

The real project contains a complex business orchestration layer.  For the
purposes of the test environment we provide a very small stand‑in that exposes
the API exercised by the tests.
"""
from datetime import date
from types import SimpleNamespace


class HistoricalContentBusinessSystem:
    """Tiny orchestrator used in tests.

    It exposes a ``config`` dict and an ``uploader`` object compatible with the
    expectations of :mod:`tests.e2e.test_daily_production_e2e`.  The
    ``run_daily_production`` method returns a dictionary containing the current
    date which allows tests to verify the call path without performing any real
    work.
    """

    def __init__(self) -> None:
        self.config = {"production_settings": {"daily_video_target": 0}}
        self.uploader = SimpleNamespace(upload_to_all_platforms=lambda **k: [])

    def run_daily_production(self) -> dict:
        return {"date": date.today().isoformat()}


__all__ = ["HistoricalContentBusinessSystem"]
