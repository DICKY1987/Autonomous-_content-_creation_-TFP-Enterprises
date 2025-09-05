import importlib
import pytest

@pytest.mark.timeout(20)
def test_research_to_script_flow(monkeypatch):
    acs = importlib.import_module("src.core.automated_content_system")
    research = acs.ContentResearchEngine()
    data = {
        "title": "Test",
        "summary": "summary",
        "url": "http://example",
        "facts": ["Fact one.", "Fact two."],
        "images": ["k1","k2","k3"],
        "categories": ["Cat"]
    }
    # Skip wiki calls
    monkeypatch.setattr(research, "research_topic", lambda topic, max_sentences=10: data)

    # Use the system which uses research internally
    cfg = acs.ContentConfig(topic="X", duration=6.0)
    sys = acs.AutomatedContentSystem(cfg, pexels_api_key=None)

    # Monkeypatch internal research call to return our data
    monkeypatch.setattr(sys, "research_engine", research)

    # Monkeypatch image manager to avoid network
    monkeypatch.setattr(sys.image_manager, "get_images_for_topic", lambda *a, **k: ["https://img/1","https://img/2","https://img/3"])
    monkeypatch.setattr(sys.image_manager, "download_image", lambda url, fp: False)
    # Monkeypatch TTS
    monkeypatch.setattr(sys.voice_synthesizer, "generate_voiceover", lambda *a, **k: True)

    ok, result = sys.create_content("Test X")
    assert ok
    assert "qa_report" in result
    assert "script" in result and len(result["script"]) > 0
