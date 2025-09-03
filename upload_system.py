#!/usr/bin/env python3
"""
Multi-Platform Upload System
Handles automated uploading to YouTube, TikTok, Instagram, etc.

Dependencies:
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
pip install requests pillow
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

# Google API
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Other APIs
import requests
from PIL import Image

logger = logging.getLogger(__name__)

@dataclass
class VideoMetadata:
    """Video metadata for uploads"""
    title_a: str
    title_b: str
    description: str
    tags: List[str]
    category_id: str = "27"  # Education
    privacy_status: str = "public"
    publish_at: Optional[str] = None
    thumbnail_a: Optional[str] = None
    thumbnail_b: Optional[str] = None

@dataclass
class UploadResult:
    """Result of upload operation"""
    platform: str
    success: bool
    video_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None

class MetadataGenerator:
    """Generates optimized metadata for different platforms"""
    
    def __init__(self):
        pass
    
    def generate_metadata(self, topic: str, content_data: Dict, script: str) -> VideoMetadata:
        """Generate optimized metadata for video"""
        try:
            # Generate two title variants
            title_a = self._generate_title_variant_a(topic, content_data)
            title_b = self._generate_title_variant_b(topic, content_data)
            
            # Generate description
            description = self._generate_description(topic, content_data, script)
            
            # Generate tags
            tags = self._generate_tags(topic, content_data)
            
            return VideoMetadata(
                title_a=title_a,
                title_b=title_b,
                description=description,
                tags=tags,
                publish_at=self._get_optimal_publish_time()
            )
            
        except Exception as e:
            logger.error(f"Metadata generation error: {str(e)}")
            # Fallback metadata
            return VideoMetadata(
                title_a=f"Amazing Facts About {topic}",
                title_b=f"{topic} in 30 Seconds",
                description=f"Quick facts about {topic}. #shorts #facts #education",
                tags=[topic.lower(), "facts", "shorts", "education", "amazing"]
            )
    
    def _generate_title_variant_a(self, topic: str, content_data: Dict) -> str:
        """Generate first title variant (fact-focused)"""
        templates = [
            f"5 Mind-Blowing Facts About {topic}",
            f"You Won't Believe These {topic} Facts",
            f"Amazing {topic} Facts That Will Shock You",
            f"Incredible {topic} Secrets Revealed",
            f"The Truth About {topic} Will Amaze You"
        ]
        
        # Pick template based on topic hash (consistent but varied)
        template_index = hash(topic) % len(templates)
        title = templates[template_index]
        
        # Ensure under 60 characters
        return title[:60] if len(title) > 60 else title
    
    def _generate_title_variant_b(self, topic: str, content_data: Dict) -> str:
        """Generate second title variant (curiosity-focused)"""
        templates = [
            f"What You Didn't Know About {topic}",
            f"{topic} Explained in 30 Seconds",
            f"The Real Story Behind {topic}",
            f"Hidden {topic} Facts Exposed",
            f"Why {topic} Is So Fascinating"
        ]
        
        template_index = (hash(topic) + 1) % len(templates)
        title = templates[template_index]
        
        return title[:60] if len(title) > 60 else title
    
    def _generate_description(self, topic: str, content_data: Dict, script: str) -> str:
        """Generate video description"""
        description_parts = [
            f"🔥 Discover amazing facts about {topic}!",
            "",
            "In this short video, you'll learn:",
        ]
        
        # Add key points from script
        facts = content_data.get('facts', [])[:3]
        for i, fact in enumerate(facts, 1):
            clean_fact = fact[:100] + "..." if len(fact) > 100 else fact
            description_parts.append(f"• {clean_fact}")
        
        # Add engagement and hashtags
        description_parts.extend([
            "",
            "💡 Like and follow for more amazing content!",
            "🔔 Turn on notifications so you never miss a video!",
            "",
            f"#shorts #{topic.lower().replace(' ', '')} #facts #education #amazing #viral #trending #learn"
        ])
        
        return "\n".join(description_parts)
    
    def _generate_tags(self, topic: str, content_data: Dict) -> List[str]:
        """Generate relevant tags"""
        primary_tags = [
            topic.lower(),
            f"{topic.lower()} facts",
            "shorts",
            "education",
            "amazing facts"
        ]
        
        # Add secondary tags based on content
        secondary_tags = [
            "viral",
            "trending",
            "learn",
            "knowledge",
            "interesting",
            "mind blowing",
            "did you know",
            "facts",
            "educational",
            "science"
        ]
        
        # Combine and limit to 15 tags
        all_tags = primary_tags + secondary_tags
        return all_tags[:15]
    
    def _get_optimal_publish_time(self) -> str:
        """Get optimal publish time (2 hours from now)"""
        publish_time = datetime.now() + timedelta(hours=2)
        return publish_time.strftime("%Y-%m-%dT%H:%M:%SZ")

class ThumbnailGenerator:
    """Generates A/B test thumbnails"""
    
    def __init__(self):
        self.canvas_size = (1280, 720)  # YouTube thumbnail size
    
    def generate_thumbnails(self, topic: str, image_paths: List[str], output_dir: str) -> Tuple[str, str]:
        """Generate two thumbnail variants"""
        try:
            if not image_paths:
                return None, None
            
            # Use first image as base
            base_image_path = image_paths[0]
            
            thumb_a_path = os.path.join(output_dir, "thumb_a.png")
            thumb_b_path = os.path.join(output_dir, "thumb_b.png")
            
            # Generate thumbnail A (minimal text)
            self._create_thumbnail_variant(
                base_image_path, thumb_a_path, topic, 
                style="minimal", color="#FF0000"
            )
            
            # Generate thumbnail B (more dramatic)
            self._create_thumbnail_variant(
                base_image_path, thumb_b_path, topic,
                style="dramatic", color="#00FF00"
            )
            
            return thumb_a_path, thumb_b_path
            
        except Exception as e:
            logger.error(f"Thumbnail generation error: {str(e)}")
            return None, None
    
    def _create_thumbnail_variant(self, base_image: str, output_path: str, 
                                 topic: str, style: str, color: str):
        """Create thumbnail variant using PIL"""
        try:
            # Open and resize base image
            img = Image.open(base_image)
            img = img.resize(self.canvas_size, Image.Resampling.LANCZOS)
            
            # For now, just save resized image
            # In production, add text overlays, effects, etc.
            img.save(output_path, "PNG", quality=95)
            
            logger.info(f"Thumbnail created: {output_path}")
            
        except Exception as e:
            logger.error(f"Thumbnail creation error: {str(e)}")

class YouTubeUploader:
    """Handles YouTube uploads using YouTube Data API v3"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_path: str = "youtube_credentials.json"):
        self.credentials_path = credentials_path
        self.service = None
        
    def authenticate(self) -> bool:
        """Authenticate with YouTube API"""
        try:
            creds = None
            token_path = "youtube_token.json"
            
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        logger.error(f"YouTube credentials file not found: {self.credentials_path}")
                        return False
                        
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('youtube', 'v3', credentials=creds)
            logger.info("YouTube authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"YouTube authentication error: {str(e)}")
            return False
    
    def upload_video(self, video_path: str, metadata: VideoMetadata, 
                    captions_path: Optional[str] = None) -> UploadResult:
        """Upload video to YouTube"""
        try:
            if not self.service:
                if not self.authenticate():
                    return UploadResult("youtube", False, error="Authentication failed")
            
            # Upload video
            video_id = self._upload_video_file(video_path, metadata)
            if not video_id:
                return UploadResult("youtube", False, error="Video upload failed")
            
            # Set thumbnail A initially
            if metadata.thumbnail_a:
                self._set_thumbnail(video_id, metadata.thumbnail_a)
            
            # Upload captions if available
            if captions_path and os.path.exists(captions_path):
                self._upload_captions(video_id, captions_path)
            
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            return UploadResult("youtube", True, video_id=video_id, url=video_url)
            
        except Exception as e:
            logger.error(f"YouTube upload error: {str(e)}")
            return UploadResult("youtube", False, error=str(e))
    
    def _upload_video_file(self, video_path: str, metadata: VideoMetadata) -> Optional[str]:
        """Upload video file"""
        try:
            tags = ",".join(metadata.tags) if metadata.tags else ""
            
            body = {
                'snippet': {
                    'title': metadata.title_a,
                    'description': metadata.description,
                    'tags': tags.split(',') if tags else [],
                    'categoryId': metadata.category_id
                },
                'status': {
                    'privacyStatus': metadata.privacy_status,
                    'selfDeclaredMadeForKids': False,
                    'publishAt': metadata.publish_at
                }
            }
            
            # Call the API's videos.insert method to create and upload the video
            media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)
            
            request = self.service.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            response = request.execute()
            
            if 'id' in response:
                logger.info(f"Video uploaded successfully. ID: {response['id']}")
                return response['id']
            else:
                logger.error("Video upload response missing ID")
                return None
                
        except Exception as e:
            logger.error(f"Video file upload error: {str(e)}")
            return None
    
    def _set_thumbnail(self, video_id: str, thumbnail_path: str):
        """Set video thumbnail"""
        try:
            media = MediaFileUpload(thumbnail_path, mimetype='image/png')
            self.service.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()
            
            logger.info(f"Thumbnail set for video {video_id}")
            
        except Exception as e:
            logger.error(f"Thumbnail upload error: {str(e)}")
    
    def _upload_captions(self, video_id: str, captions_path: str):
        """Upload captions"""
        try:
            body = {
                'snippet': {
                    'videoId': video_id,
                    'language': 'en',
                    'name': 'English',
                    'isDraft': False
                }
            }
            
            media = MediaFileUpload(captions_path, mimetype='application/octet-stream')
            
            self.service.captions().insert(
                part="snippet",
                body=body,
                media_body=media
            ).execute()
            
            logger.info(f"Captions uploaded for video {video_id}")
            
        except Exception as e:
            logger.error(f"Captions upload error: {str(e)}")
    
    def perform_ab_test(self, video_id: str, metadata: VideoMetadata, delay_hours: int = 2):
        """Switch to title/thumbnail B after delay for A/B testing"""
        try:
            # Schedule the switch (in production, use a task queue)
            time.sleep(delay_hours * 3600)
            
            # Update title to variant B
            self.service.videos().update(
                part="snippet",
                body={
                    "id": video_id,
                    "snippet": {
                        "title": metadata.title_b,
                        "description": metadata.description,
                        "categoryId": metadata.category_id
                    }
                }
            ).execute()
            
            # Set thumbnail B if available
            if metadata.thumbnail_b:
                self._set_thumbnail(video_id, metadata.thumbnail_b)
            
            logger.info(f"A/B test switch completed for video {video_id}")
            
        except Exception as e:
            logger.error(f"A/B test error: {str(e)}")

class MultiPlatformUploader:
    """Orchestrates uploads to multiple platforms"""
    
    def __init__(self):
        self.youtube_uploader = YouTubeUploader()
        self.metadata_generator = MetadataGenerator()
        self.thumbnail_generator = ThumbnailGenerator()
        
    def upload_to_all_platforms(self, video_path: str, topic: str, 
                               content_data: Dict, script: str,
                               image_paths: List[str], output_dir: str) -> List[UploadResult]:
        """Upload video to all configured platforms"""
        results = []
        
        try:
            # Generate metadata
            metadata = self.metadata_generator.generate_metadata(topic, content_data, script)
            
            # Generate thumbnails
            thumb_dir = os.path.join(output_dir, "thumbs")
            os.makedirs(thumb_dir, exist_ok=True)
            
            thumb_a, thumb_b = self.thumbnail_generator.generate_thumbnails(
                topic, image_paths, thumb_dir
            )
            
            metadata.thumbnail_a = thumb_a
            metadata.thumbnail_b = thumb_b
            
            # Upload to YouTube
            youtube_result = self.youtube_uploader.upload_video(
                video_path, metadata, 
                captions_path=os.path.join(output_dir, "captions", "captions.srt")
            )
            results.append(youtube_result)
            
            # TODO: Add other platforms (TikTok, Instagram, etc.)
            # Each platform would have its own uploader class
            
            # Save upload results
            results_file = os.path.join(output_dir, "upload_results.json")
            with open(results_file, 'w') as f:
                json.dump([result.__dict__ for result in results], f, indent=2)
            
            logger.info(f"Multi-platform upload completed. Results saved to {results_file}")
            
        except Exception as e:
            logger.error(f"Multi-platform upload error: {str(e)}")
            results.append(UploadResult("error", False, error=str(e)))
        
        return results

# Example usage
if __name__ == "__main__":
    # Test metadata generation
    generator = MetadataGenerator()
    content_data = {
        "title": "Leonardo da Vinci",
        "facts": ["Leonardo was born in 1452.", "He was a painter and inventor."]
    }
    
    metadata = generator.generate_metadata("Leonardo da Vinci", content_data, "Script text here")
    print(f"Title A: {metadata.title_a}")
    print(f"Title B: {metadata.title_b}")
    print(f"Description: {metadata.description}")
    print(f"Tags: {metadata.tags}")
