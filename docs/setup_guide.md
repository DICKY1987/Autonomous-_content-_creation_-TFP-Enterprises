# 🤖 Automated Content Creation System - Setup Guide

## 📋 Overview

This system creates fully automated, high-quality short-form videos (YouTube Shorts, TikTok, Instagram Reels) with minimal human intervention. It researches topics, sources images, generates voiceovers, assembles videos, performs quality checks, and uploads to multiple platforms.

## ⚡ Quick Start (5 Minutes)

### 1. Clone or Download the System
```bash
# Create project directory
mkdir automated-content-system
cd automated-content-system

# Save the main system file as 'content_system.py'
# Save the upload system file as 'upload_system.py'
```

### 2. Install Dependencies
```bash
# Install core packages
pip install moviepy wikipedia-api requests gtts pydub pillow openai google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2

# Optional: For better TTS quality
pip install edge-tts

# Optional: For FFmpeg (if not already installed)
# Windows: Download from https://ffmpeg.org/download.html
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
```

### 3. Basic Configuration
Create a `.env` file:
```bash
# Optional: Pexels API for high-quality images
PEXELS_API_KEY=your_pexels_api_key_here

# Optional: YouTube upload credentials (see setup below)
YOUTUBE_CREDENTIALS_PATH=youtube_credentials.json
```

### 4. Test Run (No API Keys Required)
```python
from content_system import AutomatedContentSystem, ContentConfig

# Basic configuration
config = ContentConfig(
    topic="Ancient Egypt",  # Will be overridden in create_content
    duration=30.0,
    canvas_width=1080,
    canvas_height=1920
)

# Create system
system = AutomatedContentSystem(config)

# Generate content (uses free APIs only)
success, result = system.create_content("Leonardo da Vinci")

if success:
    print(f"✅ Video created: {result['output_path']}")
    print(f"📁 Project folder: {result['project_root']}")
else:
    print(f"❌ Error: {result['error']}")
```

## 🔧 Full Setup Guide

### Step 1: System Requirements

**Minimum Requirements:**
- Python 3.8+
- 4GB RAM
- 2GB free disk space
- Internet connection

**Recommended:**
- Python 3.10+
- 8GB RAM
- 10GB free disk space
- Fast internet (for image downloads)

### Step 2: API Keys Setup (All Free Tiers Available)

#### A) Pexels API (Free - 200 images/hour)
1. Visit [Pexels API](https://www.pexels.com/api/)
2. Sign up for free account
3. Get API key from your profile
4. Add to `.env`: `PEXELS_API_KEY=your_key`

#### B) YouTube API (Free - 10,000 requests/day)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (OAuth 2.0)
5. Download credentials JSON
6. Save as `youtube_credentials.json` in project folder

#### C) Alternative Free APIs (No Keys Required)
- **Images**: Unsplash Source API (unlimited)
- **Text-to-Speech**: Google TTS (unlimited)
- **Research**: Wikipedia API (unlimited)

### Step 3: Project Structure

The system automatically creates this structure:
```
content_project_YYYYMMDD_HHMMSS/
├── audio/
│   └── voiceover.wav
├── media/
│   ├── scene1.jpg
│   ├── scene2.jpg
│   └── scene3.jpg
├── script/
│   └── script.txt
├── qa/
│   └── facts_report.json
├── build/
│   └── final_short.mp4
├── thumbs/
│   ├── thumb_a.png
│   └── thumb_b.png
└── logs/
    └── content_creation.log
```

### Step 4: Configuration Options

#### Content Configuration
```python
config = ContentConfig(
    topic="Your Topic",           # Main topic
    duration=30.0,               # Video length (15-60 seconds)
    canvas_width=1080,           # Video width (9:16 aspect ratio)
    canvas_height=1920,          # Video height
    fps=30,                      # Frame rate
    voice_language='en',         # TTS language ('en', 'es', 'fr', etc.)
    voice_speed=1.0,             # Speech speed (0.5-2.0)
    output_format='mp4'          # Output format
)
```

#### System Features You Can Enable/Disable
```python
# In the AutomatedContentSystem class
system = AutomatedContentSystem(
    config=config,
    pexels_api_key="your_key",    # None = use free Unsplash only
    enable_fact_checking=True,    # Quality assurance
    enable_upload=False,          # Auto-upload to platforms
    max_images=5,                 # Images per video
    max_facts=3                   # Facts per video
)
```

### Step 5: Running the System

#### Single Video Generation
```python
#!/usr/bin/env python3
from content_system import AutomatedContentSystem, ContentConfig

def create_single_video(topic):
    config = ContentConfig(topic=topic, duration=30.0)
    system = AutomatedContentSystem(config)
    
    success, result = system.create_content(topic)
    
    if success:
        print(f"✅ Video created successfully!")
        print(f"📁 Location: {result['output_path']}")
        print(f"📊 Quality Score: {result['qa_report']['facts_confidence']:.2f}")
        print(f"📄 Script: {result['script'][:100]}...")
        
        # Optional: Upload to platforms
        # upload_result = upload_to_platforms(result['output_path'], topic, result)
        
    else:
        print(f"❌ Failed: {result['error']}")

# Test with different topics
topics = [
    "The Great Wall of China",
    "Black Holes",
    "Ancient Rome",
    "Quantum Physics",
    "Ocean Mysteries"
]

for topic in topics:
    print(f"\n🎬 Creating video for: {topic}")
    create_single_video(topic)
```

#### Batch Content Generation
```python
#!/usr/bin/env python3
from content_system import AutomatedContentSystem, ContentConfig
import time

def batch_create_content(topics, delay_minutes=5):
    """Create multiple videos with delays"""
    config = ContentConfig(duration=30.0)
    system = AutomatedContentSystem(config)
    
    results = []
    
    for i, topic in enumerate(topics):
        print(f"\n📹 Creating video {i+1}/{len(topics)}: {topic}")
        
        success, result = system.create_content(topic)
        results.append((topic, success, result))
        
        if success:
            print(f"✅ Success: {result['output_path']}")
        else:
            print(f"❌ Failed: {result['error']}")
        
        # Delay between videos (be respectful to APIs)
        if i < len(topics) - 1:
            print(f"⏳ Waiting {delay_minutes} minutes...")
            time.sleep(delay_minutes * 60)
    
    return results

# Educational content batch
educational_topics = [
    "How Photosynthesis Works",
    "The Solar System",
    "DNA Structure",
    "Ancient Civilizations",
    "Climate Change",
    "Space Exploration",
    "Ocean Life",
    "Renewable Energy"
]

results = batch_create_content(educational_topics, delay_minutes=3)

# Print summary
successful = sum(1 for _, success, _ in results if success)
print(f"\n📊 Summary: {successful}/{len(results)} videos created successfully")
```

### Step 6: Multi-Platform Upload (Optional)

#### YouTube Setup
```python
from upload_system import MultiPlatformUploader

def upload_video(video_path, topic, content_data, script, image_paths, project_dir):
    uploader = MultiPlatformUploader()
    
    results = uploader.upload_to_all_platforms(
        video_path=video_path,
        topic=topic,
        content_data=content_data,
        script=script,
        image_paths=image_paths,
        output_dir=project_dir
    )
    
    for result in results:
        if result.success:
            print(f"✅ {result.platform}: {result.url}")
        else:
            print(f"❌ {result.platform}: {result.error}")
    
    return results
```

## 🎯 Business Model Implementation

### Revenue Stream Setup

#### 1. YouTube Monetization
```python
# Optimize for YouTube Shorts algorithm
config = ContentConfig(
    duration=45.0,              # Sweet spot for retention
    canvas_width=1080,
    canvas_height=1920,
    fps=30
)

# Focus on these niches for higher RPM:
high_rpm_niches = [
    "Personal Finance", "Crypto", "Real Estate",
    "Business Tips", "Tech Reviews", "Health"
]
```

#### 2. Affiliate Marketing Integration
```python
def add_affiliate_links(description, topic):
    """Add relevant affiliate links to video descriptions"""
    
    affiliate_links = {
        "books": "📚 Learn more: https://amzn.to/your-book-link",
        "tech": "🔧 Tools I use: https://your-affiliate-link.com",
        "finance": "💰 Investment app: https://your-referral-link.com"
    }
    
    # Add relevant links based on topic
    for category, link in affiliate_links.items():
        if category.lower() in topic.lower():
            description += f"\n\n{link}"
    
    return description
```

#### 3. Content Scaling Strategy
```python
# Daily content schedule
daily_schedule = {
    "Monday": ["Tech Facts", "Science Discoveries"],
    "Tuesday": ["History Mysteries", "Ancient Civilizations"],
    "Wednesday": ["Space Exploration", "Ocean Depths"],
    "Thursday": ["Amazing Animals", "Nature Facts"],
    "Friday": ["Inventions", "Future Technology"],
    "Saturday": ["Art History", "Famous Artists"],
    "Sunday": ["World Records", "Incredible Achievements"]
}

def run_daily_content_creation():
    """Run automated daily content creation"""
    import datetime
    
    today = datetime.datetime.now().strftime("%A")
    topics = daily_schedule.get(today, ["General Knowledge"])
    
    for topic in topics:
        create_single_video(topic)
        # Auto-upload with scheduling
        # Schedule social media posts
        # Update analytics dashboard
```

## 🔧 Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError"
```bash
# Reinstall all dependencies
pip install --upgrade moviepy wikipedia-api requests gtts pydub pillow

# On Windows, may need Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
```

#### 2. "FFmpeg not found"
```bash
# Windows
# Download from https://ffmpeg.org/download.html
# Add to PATH environment variable

# macOS
brew install ffmpeg

# Linux
sudo apt-get update
sudo apt-get install ffmpeg

# Alternative: Use moviepy's built-in FFmpeg
pip install moviepy[optional]
```

#### 3. "No images downloaded"
```python
# Check internet connection
# Try different topics (some may not have good images)
# Verify Pexels API key if using

# Debug image download:
from content_system import ImageAssetManager

manager = ImageAssetManager()
images = manager.get_images_for_topic(["test"], 1)
print(f"Found images: {images}")
```

#### 4. "Voice synthesis failed"
```python
# Try different TTS engine
from content_system import VoiceSynthesizer

# Test gTTS
synthesizer = VoiceSynthesizer(engine='gtts')
success = synthesizer.generate_voiceover("Test", "test.wav")
print(f"TTS Success: {success}")

# If fails, check internet connection (gTTS needs internet)
```

## 📈 Performance Optimization

### Speed Improvements
```python
# 1. Parallel processing for multiple videos
import concurrent.futures

def create_videos_parallel(topics, max_workers=3):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(create_single_video, topic) for topic in topics]
        results = [future.result() for future in futures]
    return results

# 2. Cache frequently used images
# 3. Pre-download voice models
# 4. Use SSD storage for faster video rendering
```

### Quality Improvements
```python
# 1. Use premium TTS for better voice quality
# 2. Add background music (ensure royalty-free)
# 3. Implement advanced fact-checking
# 4. Add custom branding/watermarks
# 5. Optimize thumbnail generation
```

## 🚀 Scaling to Production

### Infrastructure Considerations
- **Cloud Deployment**: AWS/GCP for unlimited scaling
- **Database**: Store content metadata, performance analytics
- **Queue System**: Redis/Celery for batch processing
- **Monitoring**: Track success rates, API usage, costs
- **Backup**: Automated backups of successful content

### Business Metrics to Track
- **Content Production**: Videos/day, success rate
- **Quality**: Average confidence score, manual review rate
- **Performance**: Views, engagement, revenue per video
- **Costs**: API costs, storage, compute time
- **ROI**: Revenue vs. total production costs

## 💡 Next Steps

1. **Start Simple**: Create your first 10 videos manually
2. **Analyze Performance**: See which topics/styles work best
3. **Automate Gradually**: Add scheduling, uploading, monitoring
4. **Scale Up**: Increase production volume, add new platforms
5. **Optimize**: Refine based on analytics and feedback

---

**Ready to get started?** Run the quick test above and create your first automated video in minutes! 🎬

Need help? Check the logs in `content_creation.log` for detailed debugging information.
