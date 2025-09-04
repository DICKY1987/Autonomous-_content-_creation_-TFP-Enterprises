#!/usr/bin/env python3
"""
Omnichannel Content Distribution System
Integrates with existing content creation engine for multi-platform optimization
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import hashlib
import aiohttp
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Import existing systems
from content_system import AutomatedContentSystem, ContentConfig
from upload_system import MultiPlatformUploader
from enhanced_content_system import EnhancedContentResearchEngine

logger = logging.getLogger(__name__)

@dataclass
class PlatformSpecs:
    """Platform-specific specifications"""
    name: str
    aspect_ratio: str
    max_duration: int
    resolution: Tuple[int, int]
    format: str
    max_file_size: int
    optimal_upload_times: List[str]
    hashtag_limit: int
    title_limit: int
    description_limit: int
    engagement_focus: str
    algorithm_factors: List[str]

@dataclass
class UniversalContent:
    """Universal content structure before platform adaptation"""
    content_id: str
    topic: str
    niche: str
    core_message: str
    verified_facts: List[str]
    base_script: str
    raw_video_path: str
    image_assets: List[str]
    research_data: Dict
    target_audience: str
    monetization_intent: bool

@dataclass
class PlatformContent:
    """Platform-optimized content"""
    platform: str
    video_path: str
    thumbnail_path: str
    title: str
    description: str
    hashtags: List[str]
    metadata: Dict
    upload_time: datetime
    optimization_score: float

class PlatformSpecsManager:
    """Manages platform-specific requirements and optimizations"""
    
    def __init__(self):
        self.platform_specs = {
            'youtube': PlatformSpecs(
                name='youtube',
                aspect_ratio='9:16',
                max_duration=60,
                resolution=(1080, 1920),
                format='mp4',
                max_file_size=15 * 1024 * 1024 * 1024,  # 15GB
                optimal_upload_times=['14:00', '18:00', '20:00'],
                hashtag_limit=15,
                title_limit=100,
                description_limit=5000,
                engagement_focus='watch_time',
                algorithm_factors=['retention', 'ctr', 'engagement', 'session_duration']
            ),
            'tiktok': PlatformSpecs(
                name='tiktok',
                aspect_ratio='9:16',
                max_duration=180,
                resolution=(1080, 1920),
                format='mp4',
                max_file_size=287 * 1024 * 1024,  # 287MB
                optimal_upload_times=['06:00', '10:00', '19:00'],
                hashtag_limit=100,
                title_limit=150,
                description_limit=150,
                engagement_focus='completion_rate',
                algorithm_factors=['completion_rate', 'shares', 'comments', 'replays']
            ),
            'facebook': PlatformSpecs(
                name='facebook',
                aspect_ratio='9:16',
                max_duration=90,
                resolution=(1080, 1920),
                format='mp4',
                max_file_size=4 * 1024 * 1024 * 1024,  # 4GB
                optimal_upload_times=['13:00', '15:00', '18:00'],
                hashtag_limit=30,
                title_limit=255,
                description_limit=63206,
                engagement_focus='meaningful_interactions',
                algorithm_factors=['shares', 'comments', 'reactions', 'saves']
            )
        }
    
    def get_spec(self, platform: str) -> PlatformSpecs:
        """Get specifications for a platform"""
        return self.platform_specs.get(platform)
    
    def get_all_specs(self) -> Dict[str, PlatformSpecs]:
        """Get all platform specifications"""
        return self.platform_specs

class ContentAdapter:
    """Adapts universal content for specific platforms"""
    
    def __init__(self, platform_specs: PlatformSpecsManager):
        self.platform_specs = platform_specs
        self.adaptation_strategies = {
            'youtube': self._adapt_for_youtube,
            'tiktok': self._adapt_for_tiktok,
            'facebook': self._adapt_for_facebook
        }
    
    async def adapt_content(self, universal_content: UniversalContent, platform: str) -> PlatformContent:
        """Adapt universal content for specific platform"""
        
        if platform not in self.adaptation_strategies:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return await self.adaptation_strategies[platform](universal_content)
    
    async def _adapt_for_youtube(self, content: UniversalContent) -> PlatformContent:
        """Adapt content for YouTube Shorts"""
        
        spec = self.platform_specs.get_spec('youtube')
        
        # YouTube optimization: Educational, authoritative tone
        title = self._generate_youtube_title(content)
        description = self._generate_youtube_description(content)
        hashtags = self._generate_youtube_hashtags(content)
        
        # Optimize video for YouTube
        video_path = await self._optimize_video_for_platform(
            content.raw_video_path, spec, 'youtube'
        )
        
        # Generate YouTube-optimized thumbnail
        thumbnail_path = await self._generate_platform_thumbnail(
            content, 'youtube'
        )
        
        return PlatformContent(
            platform='youtube',
            video_path=video_path,
            thumbnail_path=thumbnail_path,
            title=title,
            description=description,
            hashtags=hashtags,
            metadata={
                'category_id': '27',  # Education
                'privacy_status': 'public',
                'made_for_kids': False,
                'monetization': content.monetization_intent
            },
            upload_time=self._calculate_optimal_upload_time('youtube'),
            optimization_score=self._calculate_optimization_score(content, 'youtube')
        )
    
    async def _adapt_for_tiktok(self, content: UniversalContent) -> PlatformContent:
        """Adapt content for TikTok"""
        
        spec = self.platform_specs.get_spec('tiktok')
        
        # TikTok optimization: Viral, engaging, trending
        title = self._generate_tiktok_title(content)
        hashtags = self._generate_tiktok_hashtags(content)
        
        # Optimize video for TikTok (fast-paced, engaging)
        video_path = await self._optimize_video_for_platform(
            content.raw_video_path, spec, 'tiktok'
        )
        
        # Generate TikTok-optimized cover
        thumbnail_path = await self._generate_platform_thumbnail(
            content, 'tiktok'
        )
        
        return PlatformContent(
            platform='tiktok',
            video_path=video_path,
            thumbnail_path=thumbnail_path,
            title=title,
            description=title,  # TikTok uses same text for title and description
            hashtags=hashtags,
            metadata={
                'privacy_level': 'PUBLIC_TO_EVERYONE',
                'disable_duet': False,
                'disable_comment': False,
                'disable_stitch': False,
                'allow_download': True
            },
            upload_time=self._calculate_optimal_upload_time('tiktok'),
            optimization_score=self._calculate_optimization_score(content, 'tiktok')
        )
    
    async def _adapt_for_facebook(self, content: UniversalContent) -> PlatformContent:
        """Adapt content for Facebook Reels"""
        
        spec = self.platform_specs.get_spec('facebook')
        
        # Facebook optimization: Social, shareable, discussion-focused
        title = self._generate_facebook_title(content)
        description = self._generate_facebook_description(content)
        hashtags = self._generate_facebook_hashtags(content)
        
        # Optimize video for Facebook
        video_path = await self._optimize_video_for_platform(
            content.raw_video_path, spec, 'facebook'
        )
        
        # Generate Facebook-optimized thumbnail
        thumbnail_path = await self._generate_platform_thumbnail(
            content, 'facebook'
        )
        
        return PlatformContent(
            platform='facebook',
            video_path=video_path,
            thumbnail_path=thumbnail_path,
            title=title,
            description=description,
            hashtags=hashtags,
            metadata={
                'privacy': 'EVERYONE',
                'allow_comments': True,
                'allow_shares': True,
                'crosspost_to_instagram': True
            },
            upload_time=self._calculate_optimal_upload_time('facebook'),
            optimization_score=self._calculate_optimization_score(content, 'facebook')
        )
    
    def _generate_youtube_title(self, content: UniversalContent) -> str:
        """Generate YouTube-optimized title"""
        
        # YouTube favors educational, keyword-rich titles
        templates = [
            f"5 Amazing Facts About {content.topic} You Never Knew",
            f"The Shocking Truth About {content.topic} Revealed",
            f"{content.topic} Explained in 60 Seconds",
            f"Mind-Blowing {content.topic} Facts That Will Amaze You",
            f"What You Didn't Know About {content.topic}"
        ]
        
        # Select template based on content hash for consistency
        template_index = hash(content.content_id) % len(templates)
        title = templates[template_index]
        
        # Ensure within YouTube's limit
        return title[:100] if len(title) > 100 else title
    
    def _generate_tiktok_title(self, content: UniversalContent) -> str:
        """Generate TikTok-optimized title with trending elements"""
        
        # TikTok favors trending, casual, engaging titles
        trending_starters = [
            "POV:", "Did you know", "This is crazy:", "Wait for it...",
            "No way this is real", "Mind = blown 🤯", "Tell me why",
            "I can't believe", "Plot twist:", "This hits different"
        ]
        
        starter = trending_starters[hash(content.content_id) % len(trending_starters)]
        
        # Add trending hashtags
        base_title = f"{starter} {content.core_message[:50]}..."
        
        # Add platform-specific hashtags
        trending_tags = "#fyp #viral #facts #mindblown #trending"
        
        title = f"{base_title} {trending_tags}"
        
        return title[:150]  # TikTok limit
    
    def _generate_facebook_title(self, content: UniversalContent) -> str:
        """Generate Facebook-optimized title for social sharing"""
        
        # Facebook favors social, shareable, discussion-starting titles
        social_templates = [
            f"Share this with someone who loves {content.niche} facts! 👇",
            f"Tag a friend who needs to know about {content.topic}",
            f"This {content.topic} fact will blow your mind! 🤯",
            f"Did you know this about {content.topic}? Drop a 🤯 if this surprised you!",
            f"Amazing {content.topic} fact thread 🧵"
        ]
        
        template_index = hash(content.content_id) % len(social_templates)
        return social_templates[template_index][:255]
    
    async def _optimize_video_for_platform(self, video_path: str, spec: PlatformSpecs, platform: str) -> str:
        """Optimize video for specific platform requirements"""
        
        output_path = video_path.replace('.mp4', f'_{platform}.mp4')
        
        try:
            video = VideoFileClip(video_path)
            
            # Platform-specific optimizations
            if platform == 'tiktok':
                # TikTok: Fast-paced, engaging cuts
                video = self._add_tiktok_optimizations(video)
            elif platform == 'youtube':
                # YouTube: Maintain quality, add end screen space
                video = self._add_youtube_optimizations(video)
            elif platform == 'facebook':
                # Facebook: Social-optimized, captions-friendly
                video = self._add_facebook_optimizations(video)
            
            # Ensure specs compliance
            if video.duration > spec.max_duration:
                video = video.subclip(0, spec.max_duration)
            
            # Resize if needed
            if video.size != spec.resolution:
                video = video.resize(spec.resolution)
            
            # Export with platform-optimal settings
            video.write_videofile(
                output_path,
                codec='libx264',
                bitrate='8000k',
                fps=30,
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            video.close()
            return output_path
            
        except Exception as e:
            logger.error(f"Video optimization failed for {platform}: {str(e)}")
            return video_path  # Return original if optimization fails
    
    def _add_tiktok_optimizations(self, video):
        """Add TikTok-specific optimizations"""
        # Add quick cuts, trend elements, engagement hooks
        # This is a simplified version - can be enhanced with more sophisticated editing
        return video
    
    def _add_youtube_optimizations(self, video):
        """Add YouTube-specific optimizations"""  
        # Add professional touches, maintain quality
        return video
    
    def _add_facebook_optimizations(self, video):
        """Add Facebook-specific optimizations"""
        # Add social elements, optimize for sharing
        return video

class OmnichannelOrchestrator:
    """Main orchestrator for omnichannel content distribution"""
    
    def __init__(self, content_system: AutomatedContentSystem):
        self.content_system = content_system
        self.platform_specs = PlatformSpecsManager()
        self.content_adapter = ContentAdapter(self.platform_specs)
        self.uploader = MultiPlatformUploader()
        self.analytics = CrossPlatformAnalytics()
        self.scheduler = SmartScheduler()
        
        # Distribution settings
        self.target_platforms = ['youtube', 'tiktok', 'facebook']
        self.distribution_strategy = 'balanced'  # or 'viral_first', 'authority_first'
    
    async def process_topic_to_omnichannel(self, topic: str, target_audience: str = "general") -> Dict:
        """Complete pipeline: topic → research → create → optimize → distribute"""
        
        logger.info(f"Starting omnichannel processing for topic: {topic}")
        
        # Step 1: Create universal content using existing system
        universal_content = await self._create_universal_content(topic, target_audience)
        
        if not universal_content:
            return {"error": "Failed to create universal content"}
        
        # Step 2: Adapt content for each platform
        platform_content = await self._adapt_for_all_platforms(universal_content)
        
        # Step 3: Execute strategic distribution
        distribution_results = await self._execute_omnichannel_distribution(platform_content)
        
        # Step 4: Initialize performance tracking
        await self._setup_performance_tracking(distribution_results)
        
        return {
            "success": True,
            "universal_content_id": universal_content.content_id,
            "platform_versions": len(platform_content),
            "distribution_results": distribution_results,
            "tracking_initialized": True,
            "estimated_reach": self._estimate_total_reach(distribution_results)
        }
    
    async def _create_universal_content(self, topic: str, target_audience: str) -> Optional[UniversalContent]:
        """Create universal content using existing content creation system"""
        
        try:
            # Use existing automated content system
            success, result = self.content_system.create_content(topic)
            
            if not success:
                logger.error(f"Content creation failed: {result.get('error')}")
                return None
            
            # Extract research data for omnichannel optimization
            research_data = result.get('content_data', {})
            
            # Create universal content structure
            universal_content = UniversalContent(
                content_id=hashlib.md5(f"{topic}_{datetime.now().isoformat()}".encode()).hexdigest(),
                topic=topic,
                niche=research_data.get('niche', 'education'),
                core_message=research_data.get('title', topic),
                verified_facts=research_data.get('facts', [])[:5],
                base_script=result.get('script', ''),
                raw_video_path=result.get('output_path', ''),
                image_assets=self._extract_image_paths(result.get('project_root', '')),
                research_data=research_data,
                target_audience=target_audience,
                monetization_intent=True
            )
            
            logger.info(f"Universal content created: {universal_content.content_id}")
            return universal_content
            
        except Exception as e:
            logger.error(f"Universal content creation error: {str(e)}")
            return None
    
    async def _adapt_for_all_platforms(self, universal_content: UniversalContent) -> Dict[str, PlatformContent]:
        """Adapt universal content for all target platforms"""
        
        platform_content = {}
        
        for platform in self.target_platforms:
            try:
                adapted_content = await self.content_adapter.adapt_content(
                    universal_content, platform
                )
                platform_content[platform] = adapted_content
                logger.info(f"Content adapted for {platform}: {adapted_content.optimization_score:.2f} score")
                
            except Exception as e:
                logger.error(f"Adaptation failed for {platform}: {str(e)}")
                continue
        
        return platform_content
    
    async def _execute_omnichannel_distribution(self, platform_content: Dict[str, PlatformContent]) -> Dict:
        """Execute strategic distribution across all platforms"""
        
        # Get optimal distribution schedule
        schedule = self.scheduler.calculate_distribution_schedule(
            platform_content, strategy=self.distribution_strategy
        )
        
        distribution_results = {}
        
        for platform, content in platform_content.items():
            try:
                # Upload to platform with optimized timing
                upload_result = await self._upload_to_platform(content, schedule[platform])
                distribution_results[platform] = upload_result
                
                logger.info(f"Successfully distributed to {platform}: {upload_result.get('url', 'N/A')}")
                
            except Exception as e:
                logger.error(f"Distribution failed for {platform}: {str(e)}")
                distribution_results[platform] = {"error": str(e)}
        
        return distribution_results

class SmartScheduler:
    """Smart scheduling system for optimal multi-platform distribution"""
    
    def __init__(self):
        self.optimal_times = {
            'youtube': ['14:00', '18:00', '20:00'],  # 2PM, 6PM, 8PM EST
            'tiktok': ['06:00', '10:00', '19:00'],   # 6AM, 10AM, 7PM EST  
            'facebook': ['13:00', '15:00', '18:00'] # 1PM, 3PM, 6PM EST
        }
        self.timezone = 'US/Eastern'
    
    def calculate_distribution_schedule(self, platform_content: Dict, strategy: str = 'balanced') -> Dict:
        """Calculate optimal distribution schedule based on strategy"""
        
        schedule = {}
        base_time = datetime.now()
        
        if strategy == 'viral_first':
            # Post to TikTok first for viral potential, then cascade
            schedule['tiktok'] = base_time
            schedule['facebook'] = base_time + timedelta(hours=2)
            schedule['youtube'] = base_time + timedelta(hours=4)
            
        elif strategy == 'authority_first':
            # Post to YouTube first for SEO and authority building
            schedule['youtube'] = base_time
            schedule['facebook'] = base_time + timedelta(hours=1)
            schedule['tiktok'] = base_time + timedelta(hours=3)
            
        else:  # balanced
            # Distribute evenly based on optimal times
            schedule['youtube'] = base_time
            schedule['tiktok'] = base_time + timedelta(hours=1)
            schedule['facebook'] = base_time + timedelta(hours=2)
        
        return schedule

class CrossPlatformAnalytics:
    """Cross-platform analytics and performance tracking"""
    
    def __init__(self):
        self.performance_metrics = {}
        self.optimization_insights = {}
    
    async def track_performance(self, content_id: str, platform_results: Dict) -> Dict:
        """Track performance across all platforms"""
        
        performance_data = {}
        
        for platform, result in platform_results.items():
            if result.get('success'):
                performance_data[platform] = await self._collect_platform_metrics(
                    platform, result.get('video_id')
                )
        
        # Analyze cross-platform performance
        insights = self._analyze_cross_platform_performance(performance_data)
        
        return {
            'content_id': content_id,
            'platform_performance': performance_data,
            'insights': insights,
            'optimization_recommendations': self._generate_optimization_recommendations(insights)
        }

# Example usage and integration
async def main():
    """Example of complete omnichannel workflow"""
    
    # Initialize systems
    content_config = ContentConfig(
        topic="",  # Will be set per topic
        duration=45.0,
        canvas_width=1080,
        canvas_height=1920
    )
    
    content_system = AutomatedContentSystem(content_config)
    orchestrator = OmnichannelOrchestrator(content_system)
    
    # Test topics for omnichannel distribution
    test_topics = [
        "Artificial Intelligence Breakthroughs 2025",
        "Climate Change Solutions", 
        "Space Exploration Updates",
        "Renewable Energy Innovations"
    ]
    
    results = []
    
    for topic in test_topics:
        print(f"\n🚀 Processing: {topic}")
        
        # Execute omnichannel pipeline
        result = await orchestrator.process_topic_to_omnichannel(
            topic=topic,
            target_audience="tech_enthusiasts"
        )
        
        if result.get('success'):
            print(f"✅ Successfully distributed to {result['platform_versions']} platforms")
            print(f"📊 Estimated total reach: {result['estimated_reach']:,}")
            
            # Track performance after initial distribution
            performance = await orchestrator.analytics.track_performance(
                result['universal_content_id'],
                result['distribution_results'] 
            )
            
            print(f"📈 Performance tracking initialized for {len(performance['platform_performance'])} platforms")
            
        else:
            print(f"❌ Failed: {result.get('error')}")
        
        results.append(result)
        
        # Delay between topics to respect API limits
        await asyncio.sleep(300)  # 5 minutes between topics
    
    print(f"\n🏁 Omnichannel processing completed for {len(test_topics)} topics")
    print(f"📊 Success rate: {sum(1 for r in results if r.get('success'))/len(results)*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())