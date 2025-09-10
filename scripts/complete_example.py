#!/usr/bin/env python3
"""
Complete End-to-End Automated Content Business Implementation

This script demonstrates how to:
1. Set up automated content production
2. Implement business logic for different niches
3. Scale content creation
4. Track performance and ROI
5. Optimize for maximum profitability

Run this script to see the full system in action.
"""

import os
import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from pathlib import Path

from src.core.logging_config import get_logger

# Import our custom modules (these would be the files we created above)
try:
    from src.core.content_system import AutomatedContentSystem, ContentConfig
    from src.platforms.upload_system import MultiPlatformUploader
except ImportError:
    print("⚠️ Please save the src/core/content_system.py and src/platforms/upload_system.py files first!")
    print("Then run: pip install moviepy wikipedia-api requests gtts pydub pillow google-api-python-client")
    exit(1)

class ContentBusinessManager:
    """
    Manages the complete automated content business
    Handles scheduling, analytics, optimization, and scaling
    """
    
    def __init__(self, config_file: str = "business_config.json"):
        self.config_file = config_file
        self.load_config()
        self.setup_database()
        self.setup_logging()
        
        # Initialize content system
        self.content_config = ContentConfig(
            topic="",  # Will be set per video
            duration=self.config.get('default_duration', 30.0),
            canvas_width=1080,
            canvas_height=1920,
            fps=30
        )
        
        self.content_system = AutomatedContentSystem(
            self.content_config,
            pexels_api_key=os.getenv('PEXELS_API_KEY')
        )
        
        self.uploader = MultiPlatformUploader()
    
    def load_config(self):
        """Load business configuration"""
        default_config = {
            "niches": {
                "education": {"rpm": 1.5, "priority": 1, "daily_quota": 2},
                "science": {"rpm": 1.8, "priority": 1, "daily_quota": 2}, 
                "history": {"rpm": 1.3, "priority": 2, "daily_quota": 1},
                "technology": {"rpm": 2.2, "priority": 1, "daily_quota": 2},
                "nature": {"rpm": 1.0, "priority": 3, "daily_quota": 1}
            },
            "quality_thresholds": {
                "min_fact_confidence": 0.85,
                "min_video_duration": 25,
                "max_video_duration": 60
            },
            "business_rules": {
                "max_daily_videos": 8,
                "upload_schedule_hours": [9, 12, 15, 18],
                "retry_failed_uploads": True,
                "enable_ab_testing": True
            },
            "default_duration": 35.0
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_database(self):
        """Set up SQLite database for tracking"""
        self.db_path = "content_business.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                niche TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT,
                quality_score REAL,
                upload_status TEXT DEFAULT 'pending',
                youtube_id TEXT,
                youtube_url TEXT,
                views INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0.0,
                success BOOLEAN DEFAULT TRUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                videos_created INTEGER DEFAULT 0,
                videos_uploaded INTEGER DEFAULT 0,
                total_views INTEGER DEFAULT 0,
                total_revenue REAL DEFAULT 0.0,
                avg_quality_score REAL DEFAULT 0.0,
                success_rate REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_logging(self):
        """Set up comprehensive logging"""
        self.logger = get_logger(__name__)
    
    def get_daily_topics(self) -> List[Dict]:
        """Generate daily content topics based on niche strategy"""
        topics_by_niche = {
            "education": [
                "How Photosynthesis Works", "The Water Cycle Explained", 
                "Gravity and Mass", "Chemical Reactions Basics",
                "The Scientific Method", "DNA Structure"
            ],
            "science": [
                "Black Holes Mystery", "Quantum Physics Basics",
                "The Big Bang Theory", "Evolution Evidence",
                "Climate Change Facts", "Space Exploration"
            ],
            "history": [
                "Ancient Rome Facts", "Egyptian Pyramids", 
                "World War 2 Stories", "Renaissance Art",
                "Medieval Times", "Ancient Greece"
            ],
            "technology": [
                "Artificial Intelligence", "Blockchain Explained",
                "Future of Computing", "Internet History",
                "Robot Technology", "Virtual Reality"
            ],
            "nature": [
                "Amazon Rainforest", "Ocean Mysteries",
                "Animal Migration", "Endangered Species",
                "Weather Patterns", "Mountain Formation"
            ]
        }
        
        daily_topics = []
        for niche, niche_config in self.config["niches"].items():
            quota = niche_config["daily_quota"]
            available_topics = topics_by_niche.get(niche, [])
            
            # Select topics for this niche
            for i in range(min(quota, len(available_topics))):
                daily_topics.append({
                    "topic": available_topics[i],
                    "niche": niche,
                    "priority": niche_config["priority"],
                    "expected_rpm": niche_config["rpm"]
                })
        
        # Sort by priority
        daily_topics.sort(key=lambda x: x["priority"])
        
        # Limit to max daily videos
        max_daily = self.config["business_rules"]["max_daily_videos"]
        return daily_topics[:max_daily]
    
    def create_and_track_video(self, topic_info: Dict) -> Tuple[bool, Dict]:
        """Create video and track in database"""
        topic = topic_info["topic"]
        niche = topic_info["niche"]
        
        self.logger.info(f"Creating video: {topic} (Niche: {niche})")
        
        # Create content
        success, result = self.content_system.create_content(topic)
        
        # Track in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if success:
            quality_score = result["qa_report"]["facts_confidence"]
            
            # Check quality thresholds
            if quality_score < self.config["quality_thresholds"]["min_fact_confidence"]:
                self.logger.warning(f"Video quality below threshold: {quality_score}")
                success = False
                result["error"] = f"Quality too low: {quality_score}"
            
            cursor.execute('''
                INSERT INTO videos 
                (topic, niche, file_path, quality_score, success)
                VALUES (?, ?, ?, ?, ?)
            ''', (topic, niche, 
                  result.get("output_path", ""), 
                  quality_score, 
                  success))
        else:
            cursor.execute('''
                INSERT INTO videos 
                (topic, niche, success)
                VALUES (?, ?, ?)
            ''', (topic, niche, False))
        
        video_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        result["video_id"] = video_id
        result["niche"] = niche
        
        return success, result
    
    def upload_video(self, video_result: Dict) -> bool:
        """Upload video to platforms and update database"""
        try:
            video_path = video_result["output_path"]
            topic = video_result["content_data"]["title"]
            project_root = Path(video_result["project_root"])
            
            # Get image paths for thumbnail generation
            media_dir = project_root / "media"
            image_paths = [str(p) for p in media_dir.glob("*.jpg")]
            
            # Upload to platforms
            upload_results = self.uploader.upload_to_all_platforms(
                video_path=video_path,
                topic=topic,
                content_data=video_result["content_data"],
                script=video_result["script"],
                image_paths=image_paths,
                output_dir=str(project_root)
            )
            
            # Update database with upload results
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            youtube_result = next((r for r in upload_results if r.platform == "youtube"), None)
            
            if youtube_result and youtube_result.success:
                cursor.execute('''
                    UPDATE videos 
                    SET upload_status = 'uploaded', 
                        youtube_id = ?, 
                        youtube_url = ?
                    WHERE id = ?
                ''', (youtube_result.video_id, youtube_result.url, video_result["video_id"]))
                
                upload_success = True
                self.logger.info(f"Video uploaded successfully: {youtube_result.url}")
            else:
                cursor.execute('''
                    UPDATE videos 
                    SET upload_status = 'failed'
                    WHERE id = ?
                ''', (video_result["video_id"],))
                
                upload_success = False
                self.logger.error("Video upload failed")
            
            conn.commit()
            conn.close()
            
            return upload_success
            
        except Exception as e:
            self.logger.error(f"Upload error: {str(e)}")
            return False
    
    def run_daily_production(self) -> Dict:
        """Run complete daily content production"""
        start_time = datetime.now()
        self.logger.info("Starting daily content production...")
        
        # Get today's topics
        daily_topics = self.get_daily_topics()
        
        results = {
            "total_planned": len(daily_topics),
            "created": 0,
            "uploaded": 0,
            "failed": 0,
            "topics_processed": [],
            "errors": []
        }
        
        for i, topic_info in enumerate(daily_topics):
            self.logger.info(f"Processing {i+1}/{len(daily_topics)}: {topic_info['topic']}")
            
            try:
                # Create video
                success, video_result = self.create_and_track_video(topic_info)
                
                if success:
                    results["created"] += 1
                    
                    # Upload video
                    if self.config["business_rules"].get("auto_upload", True):
                        upload_success = self.upload_video(video_result)
                        if upload_success:
                            results["uploaded"] += 1
                        else:
                            results["errors"].append(f"Upload failed: {topic_info['topic']}")
                    
                    results["topics_processed"].append({
                        "topic": topic_info["topic"],
                        "niche": topic_info["niche"],
                        "success": True,
                        "quality": video_result["qa_report"]["facts_confidence"],
                        "path": video_result.get("output_path", "")
                    })
                    
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Creation failed: {topic_info['topic']}")
                    
                    results["topics_processed"].append({
                        "topic": topic_info["topic"],
                        "niche": topic_info["niche"],
                        "success": False,
                        "error": video_result.get("error", "Unknown error")
                    })
                
                # Delay between videos (API rate limiting)
                if i < len(daily_topics) - 1:
                    delay_minutes = 2
                    self.logger.info(f"Waiting {delay_minutes} minutes before next video...")
                    time.sleep(delay_minutes * 60)
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Exception for {topic_info['topic']}: {str(e)}")
                self.logger.error(f"Exception processing {topic_info['topic']}: {str(e)}")
        
        # Calculate metrics
        end_time = datetime.now()
        duration = end_time - start_time
        
        results["duration_minutes"] = duration.total_seconds() / 60
        results["success_rate"] = results["created"] / results["total_planned"] if results["total_planned"] > 0 else 0
        
        # Update daily metrics in database
        self.update_daily_metrics(results)
        
        self.logger.info(f"Daily production completed: {results['created']}/{results['total_planned']} videos created")
        
        return results
    
    def update_daily_metrics(self, results: Dict):
        """Update daily performance metrics in database"""
        today = datetime.now().date()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate average quality score
        successful_videos = [t for t in results["topics_processed"] if t["success"]]
        avg_quality = 0.0
        if successful_videos:
            avg_quality = sum(t.get("quality", 0) for t in successful_videos) / len(successful_videos)
        
        cursor.execute('''
            INSERT OR REPLACE INTO performance_metrics 
            (date, videos_created, videos_uploaded, avg_quality_score, success_rate)
            VALUES (?, ?, ?, ?, ?)
        ''', (today, results["created"], results["uploaded"], avg_quality, results["success_rate"]))
        
        conn.commit()
        conn.close()
    
    def get_performance_summary(self, days: int = 7) -> Dict:
        """Get performance summary for last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now().date() - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_videos,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_videos,
                AVG(quality_score) as avg_quality,
                SUM(views) as total_views,
                SUM(revenue) as total_revenue
            FROM videos 
            WHERE date(created_at) >= ?
        ''', (start_date,))
        
        row = cursor.fetchone()
        
        summary = {
            "period_days": days,
            "total_videos": row[0] or 0,
            "successful_videos": row[1] or 0,
            "success_rate": (row[1] / row[0]) if row[0] > 0 else 0,
            "avg_quality": row[2] or 0,
            "total_views": row[3] or 0,
            "total_revenue": row[4] or 0,
            "estimated_monthly_revenue": (row[4] or 0) * (30 / days)
        }
        
        conn.close()
        return summary

def main():
    """Main execution function - demonstrates complete workflow"""
    
    print("🤖 Automated Content Creation Business System")
    print("=" * 50)
    
    # Initialize business manager
    business = ContentBusinessManager()
    
    # Show current configuration
    print(f"📊 Business Configuration:")
    print(f"   - Niches: {list(business.config['niches'].keys())}")
    print(f"   - Daily quota: {business.config['business_rules']['max_daily_videos']} videos")
    print(f"   - Quality threshold: {business.config['quality_thresholds']['min_fact_confidence']}")
    
    # Get performance summary
    summary = business.get_performance_summary(7)
    print(f"\n📈 Last 7 days performance:")
    print(f"   - Videos created: {summary['total_videos']}")
    print(f"   - Success rate: {summary['success_rate']:.1%}")
    print(f"   - Average quality: {summary['avg_quality']:.2f}")
    print(f"   - Estimated monthly revenue: ${summary['estimated_monthly_revenue']:.2f}")
    
    # Show today's planned content
    daily_topics = business.get_daily_topics()
    print(f"\n📅 Today's content plan ({len(daily_topics)} videos):")
    for i, topic_info in enumerate(daily_topics, 1):
        print(f"   {i}. {topic_info['topic']} ({topic_info['niche']}) - Est. RPM: ${topic_info['expected_rpm']}")
    
    # Ask user if they want to proceed with production
    response = input(f"\n🎬 Start content production? (y/n): ").lower().strip()
    
    if response == 'y':
        print("\n🚀 Starting automated content production...")
        results = business.run_daily_production()
        
        # Show results
        print(f"\n✅ Production completed!")
        print(f"   - Created: {results['created']}/{results['total_planned']} videos")
        print(f"   - Uploaded: {results['uploaded']} videos") 
        print(f"   - Success rate: {results['success_rate']:.1%}")
        print(f"   - Duration: {results['duration_minutes']:.1f} minutes")
        
        if results['errors']:
            print(f"\n⚠️  Errors encountered:")
            for error in results['errors']:
                print(f"   - {error}")
        
        # Show successful videos
        successful = [t for t in results['topics_processed'] if t['success']]
        if successful:
            print(f"\n🎯 Successfully created videos:")
            for video in successful:
                print(f"   ✅ {video['topic']} (Quality: {video['quality']:.2f})")
                print(f"      📁 {video['path']}")
        
    else:
        print("\n👍 Production cancelled. System is ready when you are!")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Check video quality in the generated folders")
    print(f"   2. Set up YouTube API for automated uploads")
    print(f"   3. Add more niches to business_config.json")
    print(f"   4. Schedule this script to run daily")
    print(f"   5. Monitor performance in content_business.db")

if __name__ == "__main__":
    main()
