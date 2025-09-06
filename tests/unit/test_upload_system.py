import importlib
import pytest

def test_metadata_generator_smoke():
    m = importlib.import_module("src.platforms.upload_system")
    Meta = getattr(m, "MetadataGenerator")
    gen = Meta()
    md = gen.generate_metadata("Test Topic", {"facts": ["a","b","c"]}, "Some script")
    assert md.title_a and md.title_b and isinstance(md.tags, list)

def test_thumbnail_generator_api():
    m = importlib.import_module("src.platforms.upload_system")
    Thumb = getattr(m, "ThumbnailGenerator")
    t = Thumb()
    assert hasattr(t, "generate_thumbnails")


def test_multi_platform_uploader_returns_all_platforms(tmp_path):
    m = importlib.import_module("src.platforms.upload_system")
    Uploader = getattr(m, "MultiPlatformUploader")
    uploader = Uploader()
    video = tmp_path / "video.mp4"
    video.write_bytes(b"data")
    results = uploader.upload_to_all_platforms(
        video_path=str(video),
        topic="History",
        content_data={"facts": []},
        script="",
        image_paths=[],
        output_dir=str(tmp_path),
    )
    platforms = {r.platform for r in results}
    assert {"youtube", "tiktok", "instagram"} <= platforms
