import importlib
import sys
import types

# Provide minimal stubs for external dependencies to allow module import
sys.modules.setdefault("requests", types.ModuleType("requests"))

wikipedia_stub = types.ModuleType("wikipediaapi")
wikipedia_stub.Wikipedia = type("Wikipedia", (), {})
sys.modules.setdefault("wikipediaapi", wikipedia_stub)

gtts_stub = types.ModuleType("gtts")
class _DummyTTS:
    def __init__(self, *a, **k):
        pass
    def save(self, *a, **k):
        pass
gtts_stub.gTTS = _DummyTTS
sys.modules.setdefault("gtts", gtts_stub)

moviepy_pkg = types.ModuleType("moviepy")
editor_stub = types.ModuleType("moviepy.editor")
class _DummyClip:
    w = h = duration = 0
    reader = types.SimpleNamespace(codec="h264")
    def close(self):
        pass
editor_stub.VideoFileClip = _DummyClip
moviepy_pkg.editor = editor_stub
sys.modules.setdefault("moviepy", moviepy_pkg)
sys.modules.setdefault("moviepy.editor", editor_stub)

pil_pkg = types.ModuleType("PIL")
pil_image = types.ModuleType("PIL.Image")
pil_pkg.Image = pil_image
sys.modules.setdefault("PIL", pil_pkg)
sys.modules.setdefault("PIL.Image", pil_image)


def get_quality_assurance():
    m = importlib.import_module("src.core.content_system")
    return getattr(m, "QualityAssurance")()


def test_video_metadata_validation(monkeypatch):
    qa = get_quality_assurance()

    def fake_meta(path):
        return {"width": 320, "height": 240, "duration": 10, "codec": "h264"}

    monkeypatch.setattr(qa, "_get_video_metadata", fake_meta)

    content = {
        "video_path": "dummy.mp4",
        "image_meta": [{"url": "http://img", "license": "CC0"}],
        "voice_meta": {"source_url": "http://voice", "license": "CC0"},
        "max_duration": 60,
    }

    report = qa.verify_content(content, "This is a test script.")
    assert not report.technical_compliance
    assert any("resolution" in issue.lower() for issue in report.issues)


def test_license_verification(monkeypatch):
    qa = get_quality_assurance()

    def good_meta(path):
        return {"width": 1080, "height": 1920, "duration": 30, "codec": "h264"}

    monkeypatch.setattr(qa, "_get_video_metadata", good_meta)

    content = {
        "video_path": "dummy.mp4",
        "image_meta": [{"url": "http://img", "license": ""}],
        "voice_meta": {"source_url": "http://voice", "license": ""},
        "max_duration": 60,
    }

    report = qa.verify_content(content, "Clean script")
    assert not report.technical_compliance
    assert report.copyright_status == "uncertain"
    assert any("license" in issue.lower() for issue in report.issues)
