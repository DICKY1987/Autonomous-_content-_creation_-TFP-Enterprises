#!/usr/bin/env python3
"""
Main Historical Content Creation System
Orchestrates the complete pipeline for Black American history educational content
"""

import os
import json
import time
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Import our specialized modules
from src.specialized.black_history_content_system.scripts.historical_research_engine import HistoricalResearchEngine
from src.specialized.black_history_content_system.scripts.historical_script_generator import HistoricalScriptGenerator
from src.specialized.black_history_content_system.scripts.historical_qa_system import HistoricalQualityAssurance
from src.core.content_system import AutomatedContentSystem, ContentConfig
from src.platforms.upload_system import MultiPlatformUploader

class HistoricalContentBusinessSystem:
    """Complete system for creating historical educational content"""
    
    def __init__(self):
        self.setup_logging()
        self.load_configuration()
        self.load_historical_database()
        self.setup_database()
        self.initialize_engines()
        
        # Track daily content creation
        self.daily_stats = {
            "videos_created": 0,
            "videos_approved": 0,
            "total_quality_score": 0.0,
            "figures_covered": []
        }
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/historical_content.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Historical Content System initialized")
    
    def load_configuration(self):
        """Load system configuration"""
        with open("config/black_history_config.json", 'r') as f:
            self.config = json.load(f)
        self.logger.info("Configuration loaded successfully")
    
    def load_historical_database(self):
        """Load historical figures database"""
        with open("data/topics/historical_figures.json", 'r') as f:
            self.figures_db = json.load(f)
        
        # Flatten all figures into a single list for easier processing
        self.all_figures = []
        for category, figures in self.figures_db.items():
            for figure in figures:
                figure["category"] = category
                self.all_figures.append(figure)
        
        self.logger.info(f"Loaded {len(self.all_figures)} historical figures")
    
    def setup_database(self):
        """Setup SQLite database for tracking"""
        self.db_path = "data/historical_content_tracking.db"
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_production (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                figure_name TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                research_score REAL,
                quality_score REAL,
                sensitivity_score REAL,
                educational_score REAL,
                approved BOOLEAN,
                video_path TEXT,
                script_text TEXT,
                upload_status TEXT DEFAULT 'pending',
                youtube_id TEXT,
                performance_metrics TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                date DATE PRIMARY KEY,
                videos_created INTEGER,
                videos_approved INTEGER,
                avg_quality_score REAL,
                categories_covered TEXT,
                educational_impact_score REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info("Database setup completed")
    
    def initialize_engines(self):
        """Initialize all content creation engines"""
        self.research_engine = HistoricalResearchEngine()
        self.script_generator = HistoricalScriptGenerator()
        self.qa_system = HistoricalQualityAssurance()
        
        # Configure content system for historical content
        self.content_config = ContentConfig(
            topic="",  # Will be set per figure
            duration=self.config["production_settings"]["video_length"],
            canvas_width=1080,
            canvas_height=1920,
            fps=30,
            voice_language='en',
            voice_speed=0.9  # Slightly slower for educational content
        )
        
        self.content_system = AutomatedContentSystem(
            self.content_config,
            pexels_api_key=os.getenv('PEXELS_API_KEY')
        )
        
        self.uploader = MultiPlatformUploader()
        self.logger.info("All engines initialized successfully")
    
    def select_daily_figures(self, count: int = 3) -> List[Dict]:
        """Select historical figures for daily content creation"""
        try:
            # Get figures not covered recently
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get figures covered in last 30 days
            cursor.execute('''
                SELECT figure_name FROM content_production 
                WHERE created_at > datetime('now', '-30 days')
            ''')
            recent_figures = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            # Filter out recent figures
            available_figures = [f for f in self.all_figures if f["name"] not in recent_figures]
            
            if len(available_figures) < count:
                # Include some recent figures if we don't have enough
                available_figures = self.all_figures
            
            # Prioritize by educational value and diversity
            prioritized_figures = self._prioritize_figures(available_figures, count)
            
            self.logger.info(f"Selected {len(prioritized_figures)} figures for content creation")
            return prioritized_figures
            
        except Exception as e:
            self.logger.error(f"Error selecting figures: {str(e)}")
            # Fallback to first few figures
            return self.all_figures[:count]
    
    def _prioritize_figures(self, figures: List[Dict], count: int) -> List[Dict]:
        """Prioritize figures based on educational value and category diversity"""
        scored_figures = []
        
        for figure in figures:
            score = 0
            
            # High educational value gets priority
            if figure.get("educational_value") == "high":
                score += 3
            elif figure.get("educational_value") == "medium":
                score += 2
            else:
                score += 1
            
            # Diversity bonus for different categories
            category_bonus = {
                "freedom_fighters": 3,  # High priority
                "intellectuals_writers": 2,
                "inventors_innovators": 2,
                "underground_railroad": 2,
                "religious_leaders": 1
            }
            score += category_bonus.get(figure.get("category", ""), 1)
            
            # Prefer figures with rich historical records
            if len(figure.get("key_facts", [])) >= 4:
                score += 1
            
            scored_figures.append((score, figure))
        
        # Sort by score and return top figures
        scored_figures.sort(reverse=True, key=lambda x: x[0])
        return [figure for _, figure in scored_figures[:count]]
    
    def create_historical_content(self, figure_data: Dict) -> Tuple[bool, Dict]:
        """Create complete historical content for one figure"""
        figure_name = figure_data["name"]
        self.logger.info(f"Creating content for {figure_name}")
        
        try:
            # Step 1: Enhanced historical research
            self.logger.info("Step 1: Conducting historical research...")
            research_result = self.research_engine.research_historical_figure(figure_data)
            
            if "error" in research_result:
                return False, {"error": f"Research failed: {research_result['error']}"}
            
            # Step 2: Generate sensitive script
            self.logger.info("Step 2: Generating educational script...")
            script = self.script_generator.generate_script(research_result)
            
            # Step 3: Quality assurance review
            self.logger.info("Step 3: Quality assurance review...")
            qa_report = self.qa_system.evaluate_content(research_result, script)
            
            if not qa_report.approved_for_publication:
                self.logger.warning(f"Content not approved for {figure_name}")
                return False, {
                    "error": "Content did not meet quality standards",
                    "qa_report": qa_report.__dict__,
                    "issues": qa_report.issues
                }
            
            # Step 4: Create video assets
            self.logger.info("Step 4: Creating video assets...")
            content_success, content_result = self.content_system.create_content(figure_name)
            
            if not content_success:
                return False, {"error": f"Video creation failed: {content_result.get('error')}"}
            
            # Step 5: Replace generic script with our historical script
            self.logger.info("Step 5: Updating with historical script...")
            project_root = Path(content_result["project_root"])
            script_file = project_root / "script" / "script.txt"
            
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)
            
            # Step 6: Regenerate video with historical script
            self.logger.info("Step 6: Regenerating video with historical script...")
            voice_path = project_root / "audio" / "voiceover_historical.wav"
            
            if self.content_system.voice_synthesizer.generate_voiceover(
                script, str(voice_path), speed=0.9
            ):
                # Get image paths for video assembly
                media_dir = project_root / "media"
                image_paths = [str(p) for p in media_dir.glob("*.jpg")]
                
                # Assemble final video with historical script
                final_video_path = project_root / "build" / "historical_final.mp4"
                video_success = self.content_system.video_engine.create_video(
                    script, image_paths, str(voice_path), str(final_video_path)
                )
                
                if video_success:
                    content_result["output_path"] = str(final_video_path)
                else:
                    self.logger.warning("Failed to create video with historical script, using original")
            
            # Step 7: Track in database
            self._track_content_creation(
                figure_data, research_result, qa_report, script, content_result
            )
            
            # Prepare final result
            final_result = {
                "success": True,
                "figure_name": figure_name,
                "category": figure_data.get("category", "unknown"),
                "output_path": content_result["output_path"],
                "project_root": content_result["project_root"],
                "script": script,
                "research_data": research_result,
                "qa_report": qa_report.__dict__,
                "educational_value": figure_data.get("educational_value", "medium")
            }
            
            self.daily_stats["videos_created"] += 1
            self.daily_stats["videos_approved"] += 1
            self.daily_stats["total_quality_score"] += qa_report.overall_score
            self.daily_stats["figures_covered"].append(figure_name)
            
            self.logger.info(f"Successfully created content for {figure_name}")
            return True, final_result
            
        except Exception as e:
            self.logger.error(f"Content creation failed for {figure_name}: {str(e)}")
            return False, {"error": str(e)}
    
    def _track_content_creation(self, figure_data: Dict, research_result: Dict,
                              qa_report, script: str, content_result: Dict):
        """Track content creation in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO content_production 
                (figure_name, category, research_score, quality_score, 
                 sensitivity_score, educational_score, approved, video_path, script_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                figure_data["name"],
                figure_data.get("category", "unknown"),
                research_result.get("verification_score", 0.0),
                qa_report.overall_score,
                qa_report.cultural_sensitivity,
                qa_report.educational_value,
                qa_report.approved_for_publication,
                content_result.get("output_path", ""),
                script
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Database tracking error: {str(e)}")
    
    def run_daily_production(self) -> Dict:
        """Run complete daily content production"""
        start_time = datetime.now()
        self.logger.info("Starting daily historical content production")
        
        # Reset daily stats
        self.daily_stats = {
            "videos_created": 0,
            "videos_approved": 0, 
            "total_quality_score": 0.0,
            "figures_covered": []
        }
        
        # Select figures for today
        target_count = self.config["production_settings"]["daily_video_target"]
        selected_figures = self.select_daily_figures(target_count)
        
        results = {
            "date": datetime.now().date().isoformat(),
            "planned_figures": len(selected_figures),
            "successful_videos": [],
            "failed_videos": [],
            "total_quality_score": 0.0,
            "categories_covered": set(),
            "errors": []
        }
        
        # Process each figure
        for i, figure_data in enumerate(selected_figures):
            self.logger.info(f"Processing {i+1}/{len(selected_figures)}: {figure_data['name']}")
            
            try:
                success, result = self.create_historical_content(figure_data)
                
                if success:
                    results["successful_videos"].append({
                        "name": figure_data["name"],
                        "category": figure_data.get("category", "unknown"),
                        "quality_score": result["qa_report"]["overall_score"],
                        "educational_value": result["educational_value"],
                        "video_path": result["output_path"]
                    })
                    
                    results["total_quality_score"] += result["qa_report"]["overall_score"]
                    results["categories_covered"].add(figure_data.get("category", "unknown"))
                    
                else:
                    results["failed_videos"].append({
                        "name": figure_data["name"],
                        "error": result.get("error", "Unknown error"),
                        "issues": result.get("issues", [])
                    })
                    results["errors"].append(f"{figure_data['name']}: {result.get('error', 'Unknown error')}")
                
                # Delay between videos (respectful to APIs)
                if i < len(selected_figures) - 1:
                    self.logger.info("Pausing between video creation...")
                    time.sleep(120)  # 2 minute delay
                
            except Exception as e:
                error_msg = f"Exception processing {figure_data['name']}: {str(e)}"
                self.logger.error(error_msg)
                results["errors"].append(error_msg)
                results["failed_videos"].append({
                    "name": figure_data["name"],
                    "error": str(e)
                })
        
        # Calculate final metrics
        results["categories_covered"] = list(results["categories_covered"])
        results["success_rate"] = len(results["successful_videos"]) / len(selected_figures) if selected_figures else 0
        results["average_quality"] = (results["total_quality_score"] / len(results["successful_videos"]) 
                                    if results["successful_videos"] else 0.0)
        
        # Update daily metrics in database
        self._update_daily_metrics(results)
        
        end_time = datetime.now()
        results["duration_minutes"] = (end_time - start_time).total_seconds() / 60
        
        self.logger.info(f"Daily production completed: {len(results['successful_videos'])}/{len(selected_figures)} videos created")
        
        return results
    
    def _update_daily_metrics(self, results: Dict):
        """Update daily metrics in database"""
        try:
            today = datetime.now().date()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO daily_metrics 
                (date, videos_created, videos_approved, avg_quality_score, 
                 categories_covered, educational_impact_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                today,
                len(results["successful_videos"]),
                len(results["successful_videos"]),  # All successful videos are pre-approved by QA
                results["average_quality"],
                json.dumps(results["categories_covered"]),
                results["average_quality"] * len(results["successful_videos"])  # Impact metric
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Daily metrics update error: {str(e)}")
    
    def get_production_summary(self, days: int = 7) -> Dict:
        """Get production summary for reporting"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent production stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_videos,
                    COUNT(CASE WHEN approved = 1 THEN 1 END) as approved_videos,
                    AVG(quality_score) as avg_quality,
                    AVG(sensitivity_score) as avg_sensitivity,
                    AVG(educational_score) as avg_educational
                FROM content_production 
                WHERE created_at > datetime('now', '-{} days')
            '''.format(days))
            
            row = cursor.fetchone()
            
            # Get category distribution
            cursor.execute('''
                SELECT category, COUNT(*) 
                FROM content_production 
                WHERE created_at > datetime('now', '-{} days')
                GROUP BY category
            '''.format(days))
            
            categories = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "period_days": days,
                "total_videos": row[0] or 0,
                "approved_videos": row[1] or 0,
                "approval_rate": (row[1] / row[0]) if row[0] > 0 else 0,
                "average_quality": row[2] or 0,
                "average_sensitivity": row[3] or 0,
                "average_educational_value": row[4] or 0,
                "categories_covered": categories,
                "estimated_monthly_production": (row[1] or 0) * (30 / days)
            }
            
        except Exception as e:
            self.logger.error(f"Summary generation error: {str(e)}")
            return {"error": str(e)}

def main():
    """Main execution function"""
    print("🎓 Historical Educational Content Creation System")
    print("📚 Focusing on Black American History During Slavery Era")
    print("=" * 60)
    
    # Initialize system
    system = HistoricalContentBusinessSystem()
    
    # Show system status
    print(f"📊 System Configuration:")
    print(f"   - Historical figures loaded: {len(system.all_figures)}")
    print(f"   - Daily target: {system.config['production_settings']['daily_video_target']} videos")
    print(f"   - Quality threshold: {system.config['content_standards']['historical_accuracy_threshold']}")
    print(f"   - Sensitivity review: {system.config['content_standards']['sensitivity_review']}")
    
    # Show recent performance
    summary = system.get_production_summary(7)
    print(f"\n📈 Last 7 days performance:")
    print(f"   - Videos created: {summary['total_videos']}")
    print(f"   - Quality average: {summary['average_quality']:.2f}")
    print(f"   - Sensitivity average: {summary['average_sensitivity']:.2f}")
    print(f"   - Categories covered: {list(summary['categories_covered'].keys())}")
    
    # Show today's planned figures
    planned_figures = system.select_daily_figures()
    print(f"\n📅 Today's planned content ({len(planned_figures)} videos):")
    for i, figure in enumerate(planned_figures, 1):
        print(f"   {i}. {figure['name']} ({figure.get('category', 'unknown').replace('_', ' ').title()})")
        print(f"      Achievement: {figure.get('primary_achievement', 'N/A')}")
    
    # Confirm before proceeding
    response = input(f"\n🎬 Begin historical content production? (y/n): ").lower().strip()
    
    if response == 'y':
        print("\n🚀 Starting historical content production...")
        print("⚠️ Note: This will take approximately 30-45 minutes per video")
        
        results = system.run_daily_production()
        
        # Show results
        print(f"\n✅ Production completed!")
        print(f"   - Created: {len(results['successful_videos'])}/{results['planned_figures']} videos")
        print(f"   - Success rate: {results['success_rate']:.1%}")
        print(f"   - Average quality: {results['average_quality']:.2f}")
        print(f"   - Duration: {results['duration_minutes']:.1f} minutes")
        print(f"   - Categories covered: {', '.join(results['categories_covered'])}")
        
        if results['successful_videos']:
            print(f"\n🎯 Successfully created videos:")
            for video in results['successful_videos']:
                print(f"   ✅ {video['name']} (Quality: {video['quality_score']:.2f})")
                print(f"      📁 {video['video_path']}")
        
        if results['errors']:
            print(f"\n⚠️ Issues encountered:")
            for error in results['errors']:
                print(f"   - {error}")
        
    else:
        print("\n👍 Production cancelled. System ready for future use!")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Review generated videos for quality and sensitivity")
    print(f"   2. Set up YouTube API for automated educational uploads")
    print(f"   3. Consider adding more historical figures to the database")
    print(f"   4. Schedule daily production for consistent content")
    print(f"   5. Monitor educational impact and audience feedback")

if __name__ == "__main__":
    main()
