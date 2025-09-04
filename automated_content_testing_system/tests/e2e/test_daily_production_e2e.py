import importlib
import os
import pytest

@pytest.mark.timeout(60)
def test_daily_production_safe_mode(monkeypatch):
    main = importlib.import_module("main_execution_system")
    System = getattr(main, "HistoricalContentBusinessSystem", None)
    if System is None:
        pytest.skip("HistoricalContentBusinessSystem not found")

    system = System()

    # Disable real uploads
    if hasattr(system, "uploader"):
        monkeypatch.setattr(system.uploader, "upload_to_all_platforms", lambda **k: [])

    # Clamp to 1 video for test speed
    system.config["production_settings"]["daily_video_target"] = 1

    out = system.run_daily_production()
    assert isinstance(out, dict)
    assert out.get("date")
