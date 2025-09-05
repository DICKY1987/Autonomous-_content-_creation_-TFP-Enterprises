import importlib, time, pytest

@pytest.mark.timeout(120)
def test_single_video_under_target(monkeypatch):
    acs = importlib.import_module("src.core.automated_content_system")
    cfg = acs.ContentConfig(topic="Perf Test", duration=5.0)
    sys = acs.AutomatedContentSystem(cfg, pexels_api_key=None)

    # Mock heavy network interactions
    monkeypatch.setattr(sys.research_engine, "research_topic", lambda topic, **k: {
        "title": "T", "summary": "", "url": "http://", "facts": ["A."], "images": ["k"], "categories": ["C"]
    })
    monkeypatch.setattr(sys.image_manager, "get_images_for_topic", lambda *a, **k: ["https://img/1","https://img/2"])
    monkeypatch.setattr(sys.image_manager, "download_image", lambda url, fp: False)
    monkeypatch.setattr(sys.voice_synthesizer, "generate_voiceover", lambda *a, **k: True)

    start = time.time()
    ok, _ = sys.create_content("Perf Topic")
    elapsed = time.time() - start

    assert ok
    # With mocks, we expect rapid completion. Adjust as needed for your env.
    assert elapsed < 10, f"Expected <10s with mocks, got {elapsed:.2f}s"
