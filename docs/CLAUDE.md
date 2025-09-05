# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Autonomous Content Creation TFP Enterprises** system - a comprehensive automated content generation platform that creates fully automated, high-quality short-form videos for YouTube Shorts, TikTok, Instagram Reels, and other platforms with minimal human intervention. The system researches topics, sources images, generates voiceovers, assembles videos, performs quality assurance, and handles multi-platform uploads.

## Architecture

### Core System Components
- **Content Research Engine**: Wikipedia API integration for factual content and topic research
- **Asset Generation Pipeline**: Automated image sourcing from Pexels/Unsplash APIs with relevance scoring
- **Voice Synthesis System**: Text-to-speech using gTTS, Edge TTS, and premium options like ElevenLabs
- **Video Assembly Engine**: MoviePy-based video creation with automated branding and effects
- **Quality Assurance Module**: Fact verification, technical compliance, and copyright safety
- **Multi-Platform Distribution**: APIs for YouTube, TikTok, Instagram, Facebook uploads with metadata optimization

### Business Intelligence Features
- **Revenue Optimization**: A/B testing for titles, thumbnails, and content strategies
- **Analytics Dashboard**: Performance tracking across platforms with ROI calculation  
- **Content Scheduling**: Automated daily content creation with niche-specific topics
- **Scaling Framework**: Batch production capabilities for 50+ videos per day

## Project Structure

The repository is organized into logical modules:

```
src/
├── core/                    # Core content generation systems
│   ├── content_system.py           - Main automated content generation system
│   ├── automated_content_system.py - Enhanced version with additional features
│   └── enhanced_content_system.py  - Advanced content generation with premium features
├── platforms/               # Platform-specific upload and API integrations
│   ├── upload_system.py            - Multi-platform upload and distribution system
│   └── platform_apis.py            - API integrations for social media platforms
├── research/                # Content research and fact-checking
├── quality/                 # Quality assurance and monitoring
│   └── process_guardian.py         - System monitoring and error recovery
├── business/                # Business logic and optimization
│   ├── revenue_optimization.py     - Business intelligence and analytics
│   └── omnichannel_implementation.py - Multi-platform integration system
└── specialized/             # Niche-specific content systems
    └── black_history_content_system/ - Historical educational content specialization

scripts/                     # Execution and utility scripts
├── complete_example.py             - End-to-end business implementation example
├── main_execution_system.py        - Business management and scheduling system
└── workiy_main_execution.py        - Enhanced execution system

tests/                       # Complete QA and testing suite
├── unit/                           - Unit tests for individual components
├── integration/                    - Integration tests for workflows
├── e2e/                           - End-to-end production simulation
├── nonfunctional/                 - Performance and compliance testing
└── qa_runner/                     - Test execution and scenario management

docs/                        # Documentation and strategy
├── setup_guide.md                  - Comprehensive setup and installation instructions
├── multiplatform_content_business_plan.md - Complete business plan template
├── workflow_analysis.md            - Market analysis and technical architecture
└── SOP_Sections_3.4_to_3.6.md    - Standard operating procedures

config/                      # Configuration files and data
```

## Common Commands

### Core System Setup
```bash
# Install core dependencies
pip install moviepy wikipedia-api requests gtts pydub pillow openai google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2

# Optional high-quality TTS
pip install edge-tts

# For testing environment
pip install -r tests/requirements-dev.txt
```

### Basic Content Generation
```python
# Single video generation
from src.core.content_system import AutomatedContentSystem, ContentConfig

config = ContentConfig(topic="Ancient Egypt", duration=30.0, canvas_width=1080, canvas_height=1920)
system = AutomatedContentSystem(config)
success, result = system.create_content("Leonardo da Vinci")
```

### Business Management System
```python
# Complete business automation
python scripts/complete_example.py

# Main execution system with scheduling
python scripts/main_execution_system.py

# Enhanced WORKIY system
python scripts/workiy_main_execution.py
```

### Testing Commands
```bash
# Run all tests
cd tests
make test

# Run specific test suites
make unit          # Unit tests only
make integration   # Integration tests  
make e2e          # End-to-end tests
make coverage     # Coverage reporting

# Direct pytest usage
pytest -q
pytest --cov --cov-report=term-missing
```

### Multi-Platform Upload
```python
from src.platforms.upload_system import MultiPlatformUploader

uploader = MultiPlatformUploader()
results = uploader.upload_to_all_platforms(
    video_path="path/to/video.mp4",
    topic="Your Topic",
    content_data=content_data
)
```

## Development Environment

### System Requirements
- **Minimum**: Python 3.8+, 4GB RAM, 2GB disk space
- **Recommended**: Python 3.10+, 8GB RAM, 10GB disk space
- **FFmpeg**: Required for video processing (auto-installed with MoviePy or manual installation)

### API Keys and Configuration
Create a `.env` file with:
```bash
# Optional: Pexels API for high-quality images (200 images/hour free)
PEXELS_API_KEY=your_pexels_api_key_here

# Optional: YouTube upload credentials
YOUTUBE_CREDENTIALS_PATH=youtube_credentials.json

# Optional: Premium TTS services
ELEVENLABS_API_KEY=your_key_here
AZURE_TTS_KEY=your_key_here
```

### Free Tier APIs Available
- **Wikipedia API**: Unlimited research and fact-checking
- **Unsplash Source API**: Unlimited free images  
- **Google TTS (gTTS)**: Unlimited text-to-speech
- **YouTube Data API**: 10,000 requests/day free
- **Pexels API**: 200 images/hour free tier

## Key Features and Business Model

### Revenue Streams Implementation
1. **Platform Ad Revenue**: $0.50-$3 RPM (YouTube Shorts optimization)
2. **Sponsorships**: $5-$50 per 1K views (automated integration)
3. **Affiliate Marketing**: 3-8% commission with automated link insertion
4. **Digital Products**: Course and template sales integration
5. **Services**: Custom content creation for clients

### Automation Capabilities
- **Research**: Automated fact extraction from Wikipedia with confidence scoring
- **Content Creation**: Topic → Script → Images → Voice → Video in minutes
- **Quality Assurance**: Automated fact-checking, copyright compliance, technical validation
- **Distribution**: Multi-platform uploads with optimized metadata
- **Analytics**: Performance tracking, A/B testing, ROI optimization

### Scaling Features
- **Batch Production**: Generate 50+ videos per day across multiple niches
- **Scheduling System**: Automated daily content creation with niche rotation
- **Content Variants**: A/B testing for titles, thumbnails, and descriptions
- **Performance Optimization**: Analytics-driven content strategy refinement

## Architecture Patterns

### Content Generation Pipeline
```
Topic Research → Fact Extraction → Image Selection → Script Generation → 
Voice Synthesis → Video Assembly → Quality Check → Multi-Platform Upload
```

### Quality Assurance Framework
- **Fact Verification**: Wikipedia cross-referencing with confidence scoring
- **Technical Compliance**: Video format, duration, resolution validation
- **Copyright Safety**: Image licensing verification and attribution
- **Brand Consistency**: Automated watermarking and style application

### Business Intelligence
- **Performance Analytics**: View rates, engagement metrics, revenue tracking
- **Cost Optimization**: API usage monitoring and budget management
- **Content Strategy**: Topic performance analysis and trend identification
- **Scaling Metrics**: Production capacity and quality maintenance

## Testing Strategy

The testing system provides comprehensive QA:
- **Unit Tests**: Individual component testing (research, generation, assembly)
- **Integration Tests**: End-to-end workflow validation 
- **E2E Tests**: Complete production simulation with real API calls
- **Performance Tests**: Load testing and resource utilization
- **Compliance Tests**: Copyright safety and platform policy adherence

## Error Handling and Recovery

- **API Failures**: Automatic fallback to alternative services (Pexels → Unsplash)
- **Generation Errors**: Retry logic with exponential backoff
- **Quality Issues**: Automated re-generation with parameter adjustment
- **Upload Failures**: Platform-specific retry strategies
- **Resource Management**: Temporary file cleanup and memory optimization

## Module Import Patterns

When working with this codebase, use these import patterns:

```python
# Core content generation
from src.core.content_system import AutomatedContentSystem, ContentConfig
from src.core.automated_content_system import EnhancedContentSystem
from src.core.enhanced_content_system import EnhancedContentResearchEngine

# Platform integrations
from src.platforms.upload_system import MultiPlatformUploader
from src.platforms.platform_apis import YouTubeAPI, TikTokAPI

# Quality and monitoring
from src.quality.process_guardian import ProcessGuardian

# Business logic
from src.business.revenue_optimization import RevenueOptimizer
from src.business.omnichannel_implementation import OmnichannelManager

# Specialized systems
from src.specialized.black_history_content_system.scripts.historical_research_engine import HistoricalResearchEngine
```

## Development Notes

- Built on **open-source foundation** (MoviePy, FFmpeg, Wikipedia API) for cost efficiency
- **API-first design** enables easy scaling and integration
- **Multi-platform native** architecture supports all major social media platforms
- **Quality assurance automated** reduces manual review requirements
- **Business intelligence integrated** for data-driven optimization
- **Modular architecture** allows selective feature deployment
- **Extensive testing framework** ensures production reliability
- **Clean separation of concerns** with organized module structure

The system is designed for both individual creators and businesses looking to automate content production at scale while maintaining quality and compliance standards.