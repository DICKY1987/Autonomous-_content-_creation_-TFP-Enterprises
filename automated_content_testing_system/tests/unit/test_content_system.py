import importlib
import pytest

def test_automated_content_system_imports():
    m = importlib.import_module("automated_content_system")
    assert hasattr(m, "AutomatedContentSystem") and hasattr(m, "ContentConfig")

@pytest.mark.timeout(10)
def test_create_content_smoke(monkeypatch):
    m = importlib.import_module("automated_content_system")
    ContentConfig = getattr(m, "ContentConfig")
    System = getattr(m, "AutomatedContentSystem")

    # Force image downloads to be skipped by faking URLs and downloader
    config = ContentConfig(topic="Test", duration=5.0)
    sys = System(config, pexels_api_key=None)

    # Monkeypatch image manager to return a local placeholder list
    if hasattr(sys, "image_manager"):
        monkeypatch.setattr(sys.image_manager, "get_images_for_topic", lambda kw, count=3: ["https://img/1","https://img/2","https://img/3"])
        monkeypatch.setattr(sys.image_manager, "download_image", lambda url, fp: False)  # skip downloads

    # Monkeypatch voice synth to avoid TTS call
    if hasattr(sys, "voice_synthesizer"):
        monkeypatch.setattr(sys.voice_synthesizer, "generate_voiceover", lambda *a, **k: True)

    ok, result = sys.create_content("Test Topic")
    assert ok is not None
    assert isinstance(result, dict)
    assert "script" in result
