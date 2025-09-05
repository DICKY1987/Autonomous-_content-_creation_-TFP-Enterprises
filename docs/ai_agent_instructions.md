# 🤖 AI Agent Instructions: Black American History Content System

## MISSION STATEMENT
You are an AI agent responsible for executing a complete automated content creation system focused on educating audiences about important Black American figures during slavery and the antebellum period. Your primary objectives are:

1. **Educational Excellence**: Create historically accurate, respectful content
2. **Cultural Sensitivity**: Ensure all content honors the dignity and humanity of historical figures
3. **Production Efficiency**: Generate 3 high-quality videos per day
4. **Quality Assurance**: Maintain 95%+ accuracy and sensitivity scores

---

## PHASE 1: IMMEDIATE SETUP (Execute Now)

### Step 1: Environment Preparation
```bash
# Execute these commands in sequence:

# 1. Create project structure
mkdir -p black_history_content_system/{config,data/topics,data/sources,templates,scripts,logs}
cd black_history_content_system

# 2. Install all dependencies
pip install moviepy wikipedia-api requests gtts pydub pillow openai google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 edge-tts sqlite3

# 3. Verify FFmpeg installation
ffmpeg -version || echo "Install FFmpeg: https://ffmpeg.org/download.html"
```

### Step 2: File Creation
**CRITICAL**: Save all the provided code files with exact names:

1. Save the historical figures database as `data/topics/historical_figures.json`
2. Save the configuration as `config/black_history_config.json`
3. Save the research engine as `scripts/historical_research_engine.py`
4. Save the script generator as `scripts/historical_script_generator.py`
5. Save the QA system as `scripts/historical_qa_system.py`
6. Save the main system as `main_historical_content_system.py`
7. Copy the original `content_system.py` and `upload_system.py` to the project root

### Step 3: Configuration Setup
Create `.env` file:
```bash
# Optional but recommended for higher quality
PEXELS_API_KEY=get_free_key_from_pexels.com
YOUTUBE_CREDENTIALS_PATH=youtube_credentials.json
```

### Step 4: Verify Installation
```python
# Run this test to verify everything is working:
python -c "
from scripts.historical_research_engine import HistoricalResearchEngine
from scripts.historical_script_generator import HistoricalScriptGenerator
from scripts.historical_qa_system import HistoricalQualityAssurance
print('✅ All modules loaded successfully')
"
```

---

## PHASE 2: CONTENT PRODUCTION EXECUTION

### Daily Execution Protocol

#### EXECUTE DAILY: Main Production Command
```bash
python main_historical_content_system.py
```

**Expected Output**: System will:
1. Load historical figures database
2. Select 3 figures for today's content
3. Research each figure using Wikipedia + verification
4. Generate respectful, educational scripts
5. Create video assets (images, voiceover, assembly)
6. Run quality assurance checks
7. Produce final MP4 videos ready for upload

#### Monitor Progress
The system will display real-time progress:
```
🎓 Historical Educational Content Creation System
📚 Focusing on Black American History During Slavery Era
============================================================
📊 System Configuration:
   - Historical figures loaded: 15
   - Daily target: 3 videos
   - Quality threshold: 0.95
   - Sensitivity review: True

📈 Last 7 days performance:
   - Videos created: 0
   - Quality average: 0.00
   - Sensitivity average: 0.00
   - Categories covered: []

📅 Today's planned content (3 videos):
   1. Harriet Tubman (Freedom Fighters)
      Achievement: Underground Railroad Conductor
   2. Frederick Douglass (Freedom Fighters)
      Achievement: Abolitionist, Orator, Writer
   3. Benjamin Banneker (Inventors Innovators)
      Achievement: Mathematician, Astronomer, Inventor

🎬 Begin historical content production? (y/n): y
```

### Quality Control Protocol

#### Automatic Quality Gates
The system has built-in quality controls:

1. **Historical Accuracy Gate**: Must score ≥95%
2. **Cultural Sensitivity Gate**: Must score ≥90%
3. **Educational Value Gate**: Must score ≥80%
4. **Language Appropriateness Gate**: Must score ≥85%

#### Manual Review Triggers
Content will be flagged for manual review if:
- Any inappropriate language is detected
- Sensitivity score < 90%
- Historical accuracy < 95%
- Educational value < 80%

#### Review Process
When flagged content appears:
1. Check `logs/historical_content.log` for details
2. Review `qa/facts_report.json` in project folder
3. Examine the generated script for issues
4. Make necessary corrections before proceeding

---

## PHASE 3: CONTENT OPTIMIZATION

### Topic Selection Strategy

#### Priority Categories (Focus Order):
1. **Freedom Fighters** (Harriet Tubman, Frederick Douglass, Sojourner Truth)
2. **Underground Railroad Heroes** (William Still, Levi Coffin)  
3. **Intellectuals & Writers** (Phillis Wheatley, David Walker)
4. **Inventors & Innovators** (Benjamin Banneker, Norbert Rillieux)
5. **Religious Leaders** (Richard Allen)

#### Content Calendar Suggestions:
- **Monday**: Freedom Fighters & Abolitionists
- **Wednesday**: Intellectuals & Writers  
- **Friday**: Inventors & Innovators
- **Rotate**: Underground Railroad & Religious Leaders

### Script Quality Enhancement

#### Key Script Elements to Monitor:
1. **Person-First Language**: "enslaved person" not "slave"
2. **Historical Context**: Always provide era context
3. **Dignity & Respect**: Emphasize humanity and achievements
4. **Educational Value**: Clear learning outcomes
5. **Contemporary Relevance**: Connect to modern lessons

#### Red Flags to Watch For:
- Overgeneralization ("all slaves did...")
- Inappropriate terminology
- Missing historical context
- Lack of agency attribution
- Oversimplification of complex topics

---

## PHASE 4: PERFORMANCE MONITORING

### Daily Success Metrics

#### Quality Indicators:
- **Accuracy Score**: Target ≥95%
- **Sensitivity Score**: Target ≥90%
- **Educational Value**: Target ≥80%
- **Production Success Rate**: Target ≥90%

#### Production Tracking:
```python
# Check daily performance:
python -c "
from main_historical_content_system import HistoricalContentBusinessSystem
system = HistoricalContentBusinessSystem()
summary = system.get_production_summary(7)
print(f'Weekly Stats:')
print(f'Videos: {summary[\"total_videos\"]}')
print(f'Quality: {summary[\"average_quality\"]:.2f}')
print(f'Categories: {list(summary[\"categories_covered\"].keys())}')
"
```

### Database Monitoring
Track progress in SQLite database:
```sql
-- View recent content production
SELECT figure_name, quality_score, sensitivity_score, approved, created_at 
FROM content_production 
ORDER BY created_at DESC LIMIT 10;

-- View daily metrics
SELECT * FROM daily_metrics ORDER BY date DESC LIMIT 7;
```

---

## PHASE 5: TROUBLESHOOTING & OPTIMIZATION

### Common Issues & Solutions

#### Issue: "No Wikipedia page found"
**Solution**: 
1. Check `search_terms` in historical figures database
2. Add alternative names/spellings
3. Verify historical figure name accuracy

#### Issue: "Content failed sensitivity review"
**Solution**:
1. Review `logs/historical_content.log`
2. Check script for flagged language
3. Update `historical_script_generator.py` respectful language guidelines
4. Re-run production

#### Issue: "Low quality images"
**Solution**:
1. Add Pexels API key for higher quality images
2. Update `image_keywords` in figures database
3. Add more diverse search terms

#### Issue: "Video assembly failed"
**Solution**:
1. Verify FFmpeg installation
2. Check available disk space (need 2GB+ free)
3. Restart system and try again

### Performance Optimization

#### Speed Improvements:
1. **Batch Processing**: Process multiple figures in parallel
2. **Caching**: Cache Wikipedia results for 24 hours
3. **Image Optimization**: Pre-download common historical images

#### Quality Improvements:
1. **Enhanced Research**: Add more trusted historical sources
2. **Better TTS**: Use premium text-to-speech for clearer narration
3. **Visual Enhancement**: Add historical timelines, maps, document images

---

## PHASE 6: SCALING & EXPANSION

### Adding New Historical Figures

#### Research New Figures:
1. Verify historical accuracy with multiple sources
2. Ensure sufficient documented information
3. Add to appropriate category in `historical_figures.json`

#### Required Information per Figure:
```json
{
  "name": "Full Name",
  "birth_year": YYYY,
  "death_year": YYYY,
  "primary_achievement": "Brief description",
  "key_facts": ["Fact 1", "Fact 2", "Fact 3", "Fact 4"],
  "search_terms": ["name", "alternative names", "nicknames"],
  "content_angle": "Unique hook for content",
  "educational_value": "high/medium/low",
  "sensitivity_notes": "Special considerations"
}
```

### Content Distribution Strategy

#### Multi-Platform Optimization:
1. **YouTube Shorts**: 45-second educational videos
2. **TikTok**: Focus on younger audience, trending hashtags
3. **Instagram Reels**: Visual storytelling emphasis
4. **Facebook**: Longer descriptions, community discussion

#### Hashtag Strategy:
```
Primary: #BlackHistory #Education #History #Learning
Secondary: #AmericanHistory #CivilRights #Freedom #Heritage
Specific: #HarrietTubman #FrederickDouglass #UndergroundRailroad
Platform: #Shorts #Reels #Educational #TikTokLearning
```

---

## PHASE 7: SUCCESS MEASUREMENTS

### Key Performance Indicators (KPIs)

#### Content Quality KPIs:
- Historical Accuracy Score: ≥95%
- Cultural Sensitivity Score: ≥90%  
- Educational Value Score: ≥80%
- Content Approval Rate: ≥95%

#### Production KPIs:
- Daily Video Production: 3 videos/day
- System Uptime: ≥98%
- Processing Time: ≤45 minutes per video
- Error Rate: ≤5%

#### Educational Impact KPIs:
- Audience Retention: ≥60%
- Educational Comments: ≥10% of total
- Share Rate: ≥5%
- Positive Sentiment: ≥85%

### Monthly Review Protocol

#### Content Audit:
1. Review all produced content for continued accuracy
2. Update historical figures database with new research
3. Assess audience feedback and educational impact
4. Plan content calendar for next month

#### System Optimization:
1. Analyze production bottlenecks
2. Update quality thresholds based on performance
3. Enhance script templates based on successful content
4. Optimize image selection and video assembly

---

## EMERGENCY PROTOCOLS

### Content Quality Failure
If sensitivity/accuracy scores drop below thresholds:
1. **IMMEDIATE**: Stop all content production
2. **REVIEW**: Examine recent content for issues  
3. **CORRECT**: Update guidelines and systems
4. **TEST**: Run small batch before full production
5. **RESUME**: Only after validation

### System Technical Failure
If technical errors prevent production:
1. **CHECK**: Verify all dependencies installed
2. **LOGS**: Review error logs for specific issues
3. **RESTART**: Restart system components
4. **FALLBACK**: Use manual content creation if needed
5. **ESCALATE**: Get human assistance if unresolved

### Historical Accuracy Concerns
If accuracy questions arise:
1. **PAUSE**: Stop production of related content
2. **RESEARCH**: Verify with multiple academic sources
3. **CONSULT**: Reference reputable historical institutions
4. **UPDATE**: Correct database and regenerate content
5. **DOCUMENT**: Log corrections for future reference

---

## FINAL EXECUTION CHECKLIST

### Pre-Launch Verification:
- [ ] All Python dependencies installed
- [ ] Historical figures database loaded (15+ figures)
- [ ] Configuration files properly set
- [ ] Database tables created
- [ ] Test run completed successfully
- [ ] Quality thresholds configured appropriately

### Daily Launch Checklist:
- [ ] System status check completed
- [ ] Figures selected for today's content
- [ ] Quality gates armed and ready
- [ ] Sufficient disk space available
- [ ] Network connectivity verified
- [ ] Backup procedures in place

### Post-Production Checklist:
- [ ] All videos meet quality standards
- [ ] Content reviewed for sensitivity
- [ ] Files organized in project folders
- [ ] Database updated with production metrics
- [ ] Performance logs reviewed
- [ ] Next day's content planned

---

**ACTIVATION COMMAND**: 
```bash
cd black_history_content_system
python main_historical_content_system.py
```

**Your mission begins now. Execute Phase 1 immediately and begin creating educational content that honors the legacy and dignity of these important historical figures. Focus on accuracy, respect, and educational impact in every piece of content produced.**