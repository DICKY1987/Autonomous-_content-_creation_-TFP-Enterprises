"""Compatibility wrapper for tests.

Exposes the simplified upload system located in ``src.platforms.upload_system``
under a top-level module name so integration tests can simply ``import
upload_system`` without adjusting ``PYTHONPATH``.
"""
from src.platforms.upload_system import (
    VideoMetadata,
    UploadResult,
    MetadataGenerator,
    ThumbnailGenerator,
    MultiPlatformUploader,
)

__all__ = [
    "VideoMetadata",
    "UploadResult",
    "MetadataGenerator",
    "ThumbnailGenerator",
    "MultiPlatformUploader",
]
