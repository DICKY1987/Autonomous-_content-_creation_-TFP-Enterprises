#!/usr/bin/env python3
"""
Platform-Specific API Integration Code
Ready-to-use implementations for YouTube, TikTok, and Facebook
"""

import asyncio
import aiohttp
import json
import base64
import os
from typing import Dict, List, Optional

from src.core.logging_config import get_logger
from dataclasses import dataclass
from datetime import datetime

# Google APIs for YouTube
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logger = get_logger(__name__)

@dataclass
class UploadResult:
    platform: str
    success: bool
    video_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class YouTubeAPIClient:
    """YouTube Data API v3 Client with enhanced features"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.force-ssl'
    ]
    
    def __init__(self, credentials_path: str = "youtube_credentials.json"):
        self.credentials_path = credentials_path
        self.service = None
        self.quota_usage = 0
        self.daily_quota_limit = 10000
        
    async def initialize(self):
        """Initialize YouTube API service with OAuth2"""
        try:
            creds = None
            token_path = "youtube_token.json"
            
            # Load existing token
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        raise Exception(f"YouTube credentials file not found: {self.credentials_path}")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0, prompt='consent')
                
                # Save credentials
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('youtube', 'v3', credentials=creds)
            logger.info("YouTube API initialized successfully")
            
        except Exception as e:
            logger.error(f"YouTube API initialization failed: {str(e)}")
            raise
    
    async def upload_video(self, video_path: str, metadata: Dict) -> UploadResult:
        """Upload video to YouTube with full metadata"""
        
        if not self.service:
            await self.initialize()
        
        # Check quota
        if self.quota_usage >= self.daily_quota_limit:
            return UploadResult(
                platform="youtube",
                success=False,
                error="Daily quota exceeded"
            )
        
        try:
            # Prepare request body
            body = {
                'snippet': {
                    'title': metadata.get('title', 'Untitled Video')[:100],
                    'description': metadata.get('description', '')[:5000],
                    'tags': metadata.get('tags', [])[:500],
                    'categoryId': metadata.get('category_id', '27'),  # Education
                    'defaultLanguage': 'en',
                    'defaultAudioLanguage': 'en'
                },
                'status': {
                    'privacyStatus': metadata.get('privacy_status', 'public'),
                    'selfDeclaredMadeForKids': False,
                    'publishAt': metadata.get('publish_at')
                }
            }
            
            # Prepare media upload
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True,
                chunksize=1024 * 1024 * 4  # 4MB chunks
            )
            
            # Execute upload
            request = self.service.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            response = None
            error = None
            retry_count = 0
            max_retries = 3
            
            while response is None and retry_count < max_retries:
                try:
                    status, response = request.next_chunk()
                    if response is not None:
                        if 'id' in response:
                            video_id = response['id']
                            
                            # Upload thumbnail if provided
                            if metadata.get('thumbnail_path'):
                                await self._upload_thumbnail(video_id, metadata['thumbnail_path'])
                            
                            # Upload captions if provided
                            if metadata.get('captions_path'):
                                await self._upload_captions(video_id, metadata['captions_path'])
                            
                            self.quota_usage += 1600  # Approximate quota cost
                            
                            return UploadResult(
                                platform="youtube",
                                success=True,
                                video_id=video_id,
                                url=f"https://www.youtube.com/watch?v={video_id}",
                                metadata={
                                    'quota_used': self.quota_usage,
                                    'upload_time': datetime.now().isoformat()
                                }
                            )
                        else:
                            return UploadResult(
                                platform="youtube",
                                success=False,
                                error="Upload failed - no video ID returned"
                            )
                            
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        error = str(e)
                        break
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
            
            return UploadResult(
                platform="youtube",
                success=False,
                error=error or "Upload failed after retries"
            )
            
        except Exception as e:
            logger.error(f"YouTube upload error: {str(e)}")
            return UploadResult(
                platform="youtube",
                success=False,
                error=str(e)
            )
    
    async def _upload_thumbnail(self, video_id: str, thumbnail_path: str):
        """Upload custom thumbnail"""
        try:
            media = MediaFileUpload(thumbnail_path, mimetype='image/png')
            self.service.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()
            logger.info(f"Thumbnail uploaded for video {video_id}")
        except Exception as e:
            logger.error(f"Thumbnail upload failed: {str(e)}")
    
    async def _upload_captions(self, video_id: str, captions_path: str):
        """Upload captions/subtitles"""
        try:
            body = {
                'snippet': {
                    'videoId': video_id,
                    'language': 'en',
                    'name': 'English Captions',
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
            logger.error(f"Captions upload failed: {str(e)}")

class TikTokAPIClient:
    """TikTok Content Posting API Client"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://open.tiktokapis.com/v2"
        self.session = None
        self.upload_count_today = 0
        self.max_daily_uploads = 30
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def upload_video(self, video_path: str, metadata: Dict) -> UploadResult:
        """Upload video to TikTok"""
        
        if self.upload_count_today >= self.max_daily_uploads:
            return UploadResult(
                platform="tiktok",
                success=False,
                error="Daily upload limit reached"
            )
        
        try:
            # Step 1: Initialize upload
            upload_init = await self._initialize_upload(video_path)
            if not upload_init.get('success'):
                return UploadResult(
                    platform="tiktok",
                    success=False,
                    error=upload_init.get('error', 'Upload initialization failed')
                )
            
            upload_url = upload_init['upload_url']
            publish_id = upload_init['publish_id']
            
            # Step 2: Upload video file
            upload_success = await self._upload_video_file(video_path, upload_url)
            if not upload_success:
                return UploadResult(
                    platform="tiktok",
                    success=False,
                    error="Video file upload failed"
                )
            
            # Step 3: Publish video
            publish_result = await self._publish_video(publish_id, metadata)
            
            if publish_result.get('success'):
                self.upload_count_today += 1
                
                return UploadResult(
                    platform="tiktok",
                    success=True,
                    video_id=publish_result['share_id'],
                    url=f"https://tiktok.com/@username/video/{publish_result['share_id']}",
                    metadata={
                        'uploads_remaining': self.max_daily_uploads - self.upload_count_today,
                        'upload_time': datetime.now().isoformat()
                    }
                )
            else:
                return UploadResult(
                    platform="tiktok",
                    success=False,
                    error=publish_result.get('error', 'Publication failed')
                )
                
        except Exception as e:
            logger.error(f"TikTok upload error: {str(e)}")
            return UploadResult(
                platform="tiktok",
                success=False,
                error=str(e)
            )
    
    async def _initialize_upload(self, video_path: str) -> Dict:
        """Initialize TikTok upload session"""
        
        file_size = os.path.getsize(video_path)
        chunk_size = 10 * 1024 * 1024  # 10MB
        chunk_count = (file_size + chunk_size - 1) // chunk_size
        
        payload = {
            'source_info': {
                'source': 'FILE_UPLOAD',
                'video_size': file_size,
                'chunk_size': chunk_size,
                'total_chunk_count': chunk_count
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/post/publish/inbox/video/init/",
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'upload_url': result['data']['upload_url'],
                        'publish_id': result['data']['publish_id']
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f"Init failed: {error_text}"
                    }
        except Exception as e:
            return {
                'success': False,
                'error': f"Init exception: {str(e)}"
            }
    
    async def _upload_video_file(self, video_path: str, upload_url: str) -> bool:
        """Upload video file to TikTok's storage"""
        
        try:
            with open(video_path, 'rb') as video_file:
                data = aiohttp.FormData()
                data.add_field('video', video_file, filename=os.path.basename(video_path))
                
                async with self.session.put(upload_url, data=data) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"TikTok file upload error: {str(e)}")
            return False
    
    async def _publish_video(self, publish_id: str, metadata: Dict) -> Dict:
        """Publish uploaded video with metadata"""
        
        # Optimize title for TikTok
        title = metadata.get('title', '')[:150]
        
        # Add TikTok-friendly hashtags if not present
        if '#fyp' not in title.lower():
            title += ' #fyp #viral #trending'
        
        payload = {
            'publish_id': publish_id,
            'post_info': {
                'title': title,
                'privacy_level': metadata.get('privacy_level', 'SELF_ONLY'),
                'disable_duet': metadata.get('disable_duet', False),
                'disable_comment': metadata.get('disable_comment', False),
                'disable_stitch': metadata.get('disable_stitch', False),
                'video_cover_timestamp_ms': 1000
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/post/publish/",
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'share_id': result['data']['share_id']
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f"Publish failed: {error_text}"
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f"Publish exception: {str(e)}"
            }

class FacebookAPIClient:
    """Facebook Graph API Client for Reels"""
    
    def __init__(self, access_token: str, page_id: str):
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def upload_video(self, video_path: str, metadata: Dict) -> UploadResult:
        """Upload video as Facebook Reel"""
        
        try:
            # Step 1: Initialize resumable upload
            upload_session = await self._initialize_resumable_upload(video_path, metadata)
            if not upload_session.get('success'):
                return UploadResult(
                    platform="facebook",
                    success=False,
                    error=upload_session.get('error', 'Upload session creation failed')
                )
            
            upload_session_id = upload_session['upload_session_id']
            
            # Step 2: Upload video file
            upload_success = await self._upload_video_chunks(video_path, upload_session_id)
            if not upload_success:
                return UploadResult(
                    platform="facebook",
                    success=False,
                    error="Video upload failed"
                )
            
            # Step 3: Publish video
            publish_result = await self._publish_facebook_reel(upload_session_id, metadata)
            
            if publish_result.get('success'):
                return UploadResult(
                    platform="facebook",
                    success=True,
                    video_id=publish_result['video_id'],
                    url=f"https://facebook.com/{publish_result['video_id']}",
                    metadata={
                        'upload_time': datetime.now().isoformat()
                    }
                )
            else:
                return UploadResult(
                    platform="facebook",
                    success=False,
                    error=publish_result.get('error', 'Publication failed')
                )
                
        except Exception as e:
            logger.error(f"Facebook upload error: {str(e)}")
            return UploadResult(
                platform="facebook",
                success=False,
                error=str(e)
            )
    
    async def _initialize_resumable_upload(self, video_path: str, metadata: Dict) -> Dict:
        """Initialize Facebook resumable upload session"""
        
        file_size = os.path.getsize(video_path)
        
        params = {
            'access_token': self.access_token,
            'upload_phase': 'start',
            'file_size': file_size
        }
        
        try:
            url = f"{self.base_url}/{self.page_id}/videos"
            
            async with self.session.post(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'upload_session_id': result['upload_session_id']
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f"Session init failed: {error_text}"
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f"Session init exception: {str(e)}"
            }
    
    async def _upload_video_chunks(self, video_path: str, upload_session_id: str) -> bool:
        """Upload video in chunks to Facebook"""
        
        try:
            chunk_size = 4 * 1024 * 1024  # 4MB chunks
            file_size = os.path.getsize(video_path)
            
            with open(video_path, 'rb') as video_file:
                start_offset = 0
                
                while start_offset < file_size:
                    end_offset = min(start_offset + chunk_size, file_size) - 1
                    chunk = video_file.read(chunk_size)
                    
                    params = {
                        'access_token': self.access_token,
                        'upload_phase': 'transfer',
                        'start_offset': start_offset,
                        'upload_session_id': upload_session_id
                    }
                    
                    data = aiohttp.FormData()
                    data.add_field('video_file_chunk', chunk)
                    
                    url = f"{self.base_url}/{self.page_id}/videos"
                    
                    async with self.session.post(url, params=params, data=data) as response:
                        if response.status != 200:
                            logger.error(f"Chunk upload failed: {await response.text()}")
                            return False
                    
                    start_offset += chunk_size
            
            return True
            
        except Exception as e:
            logger.error(f"Facebook chunk upload error: {str(e)}")
            return False
    
    async def _publish_facebook_reel(self, upload_session_id: str, metadata: Dict) -> Dict:
        """Publish uploaded video as Facebook Reel"""
        
        # Prepare description with hashtags
        description = metadata.get('description', '')
        hashtags = metadata.get('hashtags', [])
        
        if hashtags:
            description += ' ' + ' '.join([f'#{tag}' for tag in hashtags[:30]])
        
        params = {
            'access_token': self.access_token,
            'upload_phase': 'finish',
            'upload_session_id': upload_session_id,
            'description': description,
            'title': metadata.get('title', 'Untitled Video'),
            'privacy': json.dumps({
                'value': metadata.get('privacy', 'EVERYONE')
            }),
            'published': True
        }
        
        try:
            url = f"{self.base_url}/{self.page_id}/videos"
            
            async with self.session.post(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'video_id': result['id']
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f"Publish failed: {error_text}"
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f"Publish exception: {str(e)}"
            }

class OmnichannelUploadManager:
    """Manage uploads across all platforms"""
    
    def __init__(self):
        self.youtube_client = YouTubeAPIClient()
        self.tiktok_token = os.getenv('TIKTOK_ACCESS_TOKEN')
        self.facebook_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.facebook_page_id = os.getenv('FACEBOOK_PAGE_ID')
        
    async def upload_to_all_platforms(self, video_path: str, platform_metadata: Dict[str, Dict]) -> Dict[str, UploadResult]:
        """Upload video to all configured platforms"""
        
        results = {}
        
        # YouTube upload
        if 'youtube' in platform_metadata:
            try:
                youtube_result = await self.youtube_client.upload_video(
                    video_path, 
                    platform_metadata['youtube']
                )
                results['youtube'] = youtube_result
                logger.info(f"YouTube upload: {'✅' if youtube_result.success else '❌'}")
            except Exception as e:
                results['youtube'] = UploadResult(platform="youtube", success=False, error=str(e))
        
        # TikTok upload
        if 'tiktok' in platform_metadata and self.tiktok_token:
            try:
                async with TikTokAPIClient(self.tiktok_token) as tiktok_client:
                    tiktok_result = await tiktok_client.upload_video(
                        video_path,
                        platform_metadata['tiktok']
                    )
                    results['tiktok'] = tiktok_result
                    logger.info(f"TikTok upload: {'✅' if tiktok_result.success else '❌'}")
            except Exception as e:
                results['tiktok'] = UploadResult(platform="tiktok", success=False, error=str(e))
        
        # Facebook upload  
        if 'facebook' in platform_metadata and self.facebook_token and self.facebook_page_id:
            try:
                async with FacebookAPIClient(self.facebook_token, self.facebook_page_id) as facebook_client:
                    facebook_result = await facebook_client.upload_video(
                        video_path,
                        platform_metadata['facebook']
                    )
                    results['facebook'] = facebook_result
                    logger.info(f"Facebook upload: {'✅' if facebook_result.success else '❌'}")
            except Exception as e:
                results['facebook'] = UploadResult(platform="facebook", success=False, error=str(e))
        
        return results

# Example usage
async def main():
    """Example of using the omnichannel upload system"""
    
    # Initialize upload manager
    upload_manager = OmnichannelUploadManager()
    
    # Prepare platform-specific metadata
    platform_metadata = {
        'youtube': {
            'title': 'Amazing AI Facts That Will Blow Your Mind in 2025',
            'description': '''🤖 Discover the most incredible AI breakthroughs happening right now!
            
In this video, you'll learn:
• Revolutionary AI developments
• Mind-blowing capabilities  
• What this means for the future

💡 Subscribe for more amazing tech content!
📱 Follow us on social media for daily updates
🔔 Ring the bell for notifications!

#AI #ArtificialIntelligence #Technology #Future #Innovation #TechNews #MachineLearning #Automation #DigitalTransformation #TechTrends''',
            'tags': ['AI', 'Artificial Intelligence', 'Technology', 'Future', 'Innovation', 'Tech News', 'Machine Learning', 'Automation'],
            'category_id': '28',  # Science & Technology
            'thumbnail_path': 'thumbnail_youtube.png',
            'captions_path': 'captions.srt'
        },
        
        'tiktok': {
            'title': 'Mind-blowing AI facts that will shock you! 🤯 #AI #TechTok #FutureIsNow #viral #fyp #mindblown #technology #innovation #artificialintelligence #trending',
            'privacy_level': 'PUBLIC_TO_EVERYONE',
            'disable_duet': False,
            'disable_comment': False,
            'disable_stitch': False
        },
        
        'facebook': {
            'title': 'The Future of AI is Here - Mind-Blowing Facts!',
            'description': '''🚀 The AI revolution is happening NOW! Here are the most incredible facts about artificial intelligence that will change everything.
            
✨ What did you think of these AI facts? Share your thoughts in the comments!
            
👥 Tag a friend who loves technology!
📤 Share this with someone who needs to see this!''',
            'hashtags': ['AI', 'Technology', 'Innovation', 'Future', 'TechNews', 'Reels', 'ArtificialIntelligence', 'TechFacts'],
            'privacy': 'EVERYONE'
        }
    }
    
    # Upload video to all platforms
    video_path = "path/to/your/video.mp4"
    
    upload_results = await upload_manager.upload_to_all_platforms(
        video_path, 
        platform_metadata
    )
    
    # Print results
    print("\n🚀 Omnichannel Upload Results:")
    print("=" * 50)
    
    successful_uploads = 0
    total_platforms = len(upload_results)
    
    for platform, result in upload_results.items():
        status = "✅ SUCCESS" if result.success else "❌ FAILED"
        print(f"{platform.upper()}: {status}")
        
        if result.success:
            successful_uploads += 1
            print(f"  📹 Video ID: {result.video_id}")
            print(f"  🔗 URL: {result.url}")
        else:
            print(f"  ❌ Error: {result.error}")
        print()
    
    success_rate = (successful_uploads / total_platforms) * 100
    print(f"📊 Success Rate: {success_rate:.1f}% ({successful_uploads}/{total_platforms})")
    
    return upload_results

if __name__ == "__main__":
    # Set up environment variables first:
    # export TIKTOK_ACCESS_TOKEN="your_tiktok_token"
    # export FACEBOOK_ACCESS_TOKEN="your_facebook_token" 
    # export FACEBOOK_PAGE_ID="your_page_id"
    
    asyncio.run(main())