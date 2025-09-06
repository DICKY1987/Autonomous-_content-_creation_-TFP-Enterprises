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
            # Create empty placeholder files so downstream code expecting image
            # paths can operate without requiring Pillow or real image assets.
            with open(p, "wb") as f:
                f.write(b"")
        return thumb_a, thumb_b


class YouTubeUploader:
    """Stub uploader for YouTube."""

    def upload_video(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        return UploadResult(
            platform="youtube",
            success=True,
            video_id="YOUTUBE123",
            url="http://example.com/youtube",
        )


class TikTokUploader:
    """Stub uploader for TikTok."""

    def upload_video(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        return UploadResult(
            platform="tiktok",
            success=True,
            video_id="TIKTOK123",
            url="http://example.com/tiktok",
        )


class InstagramUploader:
    """Stub uploader for Instagram."""

    def upload_video(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        return UploadResult(
            platform="instagram",
            success=True,
            video_id="INSTA123",
            url="http://example.com/instagram",
        )


class MultiPlatformUploader:
    """Minimal uploader that uses the metadata and thumbnail generators."""

    def __init__(self):
        self.metadata_generator = MetadataGenerator()
        self.thumbnail_generator = ThumbnailGenerator()
        self.youtube_uploader = YouTubeUploader()
        self.tiktok_uploader = TikTokUploader()
        self.instagram_uploader = InstagramUploader()

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
        results = [
            self.youtube_uploader.upload_video(video_path, md),
            self.tiktok_uploader.upload_video(video_path, md),
            self.instagram_uploader.upload_video(video_path, md),
        ]
        return results


__all__ = [
    "VideoMetadata",
    "UploadResult",
    "MetadataGenerator",
    "ThumbnailGenerator",
    "MultiPlatformUploader",
]
