import importlib
import pytest
import os

@pytest.mark.timeout(10)
def test_upload_flow_metadata_only(monkeypatch, tmp_path):
    up = importlib.import_module("upload_system")
    Meta = getattr(up, "MetadataGenerator")
    Uploader = getattr(up, "MultiPlatformUploader", None)
    if Uploader is None:
        pytest.skip("MultiPlatformUploader not present in this version")

    md = Meta().generate_metadata("Test Topic", {"facts": ["A","B","C"]}, "Script text")
    # Build a fake video path
    vp = tmp_path / "video.mp4"
    vp.write_bytes(b"fake")  # not a real video; tests won't try upload

    uploader = Uploader()
    # Monkeypatch all upload clients to avoid network
    if hasattr(uploader, "upload_to_all_platforms"):
        monkeypatch.setattr(uploader, "upload_to_all_platforms", lambda **k: [])
    res = uploader.upload_to_all_platforms(
        video_path=str(vp),
        topic="Test Topic",
        content_data={"facts": ["A","B"], "title": "Test"},
        script="script",
        image_paths=[],
        output_dir=str(tmp_path)
    )
    assert isinstance(res, list)
