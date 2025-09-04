import importlib
import pytest

def test_metadata_generator_smoke():
    m = importlib.import_module("upload_system")
    Meta = getattr(m, "MetadataGenerator")
    gen = Meta()
    md = gen.generate_metadata("Test Topic", {"facts": ["a","b","c"]}, "Some script")
    assert md.title_a and md.title_b and isinstance(md.tags, list)

def test_thumbnail_generator_api():
    m = importlib.import_module("upload_system")
    Thumb = getattr(m, "ThumbnailGenerator")
    t = Thumb()
    assert hasattr(t, "generate_thumbnails")
