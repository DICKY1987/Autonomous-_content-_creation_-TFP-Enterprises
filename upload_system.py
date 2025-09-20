"""Compatibility shim for tests.

Re-exports the simplified upload system from ``src.platforms.upload_system`` so
tests can import ``upload_system`` from the project root.
"""
from src.platforms.upload_system import (  # noqa: F401
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

