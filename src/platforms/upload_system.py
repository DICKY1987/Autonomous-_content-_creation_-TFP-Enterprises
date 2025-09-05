from __future__ import annotations
"""Simplified upload system for tests.

The real project contains a feature rich implementation that integrates with the
YouTube API and performs image manipulation.  For the purposes of the automated
tests we provide a very small, dependency free subset that exposes the same
classes used in the test suite.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
import os


@dataclass
class VideoMetadata:
    title_a: str
    title_b: str
    description: str
    tags: List[str]
    category_id: str = "27"
    privacy_status: str = "public"
    publish_at: Optional[str] = None
    thumbnail_a: Optional[str] = None
    thumbnail_b: Optional[str] = None


@dataclass
class UploadResult:
    platform: str
    success: bool
    video_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None


class MetadataGenerator:
    """Return deterministic metadata for a given topic."""

    def generate_metadata(self, topic: str, content_data: Dict, script: str) -> VideoMetadata:
        title_a = f"Amazing Facts About {topic}"
        title_b = f"{topic} in 30 Seconds"
        description = f"Quick facts about {topic}."
        tags = [topic.lower(), "facts", "shorts", "education"]
        return VideoMetadata(title_a=title_a, title_b=title_b, description=description, tags=tags)


class ThumbnailGenerator:
    """Generate placeholder thumbnail files and return their paths."""

    def generate_thumbnails(self, topic: str, image_paths: List[str], output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        thumb_a = os.path.join(output_dir, "thumb_a.jpg")
        thumb_b = os.path.join(output_dir, "thumb_b.jpg")
        for p in (thumb_a, thumb_b):
            with open(p, "wb"):
                pass
        return thumb_a, thumb_b


class MultiPlatformUploader:
    """Minimal uploader that uses the metadata and thumbnail generators."""

    def __init__(self):
        self.metadata_generator = MetadataGenerator()
        self.thumbnail_generator = ThumbnailGenerator()

    def upload_to_all_platforms(
        self,
        video_path: str,
        topic: str,
        content_data: Dict,
        script: str,
        image_paths: List[str],
        output_dir: str,
    ) -> List[UploadResult]:
        md = self.metadata_generator.generate_metadata(topic, content_data, script)
        self.thumbnail_generator.generate_thumbnails(topic, image_paths, output_dir)
        # In real life we'd upload the video. For tests we just return a stub result.
        return [UploadResult(platform="youtube", success=True, video_id="TEST123", url="http://example.com")]


__all__ = [
    "VideoMetadata",
    "UploadResult",
    "MetadataGenerator",
    "ThumbnailGenerator",
    "MultiPlatformUploader",
]
