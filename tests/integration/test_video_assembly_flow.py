import importlib
import pytest

@pytest.mark.timeout(20)
def test_video_assembly_path_exists(monkeypatch):
    acs = importlib.import_module("src.core.automated_content_system")
    cfg = acs.ContentConfig(topic="Y", duration=5.0)
    sys = acs.AutomatedContentSystem(cfg, pexels_api_key=None)

    # Mock everything heavy
    monkeypatch.setattr(sys.research_engine, "research_topic", lambda topic, **k: {
        "title": "Test", "summary": "", "url": "http://", "facts": ["A."], "images": ["k"], "categories": ["C"]
    })
    monkeypatch.setattr(sys.image_manager, "get_images_for_topic", lambda *a, **k: ["https://img/1","https://img/2"])
    monkeypatch.setattr(sys.image_manager, "download_image", lambda url, fp: False)
    monkeypatch.setattr(sys.voice_synthesizer, "generate_voiceover", lambda *a, **k: True)

    ok, result = sys.create_content("Topic Y")
    assert ok
    # We don't assert real video file since mocks skip rendering, but path key should exist
    assert "output_path" in result
