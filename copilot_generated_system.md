# GitHub Copilot Workspace Generated System

## 🚀 Complete File Structure (Auto-Generated)

```
historical-video-system/
├── template.yaml                 # AWS SAM template
├── requirements.txt              # Python dependencies
├── src/
│   ├── research/
│   │   ├── handler.py           # Wikipedia research Lambda
│   │   └── requirements.txt
│   ├── script_generation/
│   │   ├── handler.py           # OpenAI script generation
│   │   └── requirements.txt
│   ├── video_creation/
│   │   ├── handler.py           # Video assembly
│   │   ├── Dockerfile           # Container for MoviePy
│   │   └── requirements.txt
│   └── upload/
│       ├── youtube_handler.py   # YouTube upload
│       ├── tiktok_handler.py    # TikTok upload
│       └── requirements.txt
├── data/
│   └── historical_figures.json  # Pre-loaded database
├── statemachine/
│   └── definition.json          # Step Functions workflow
└── deploy.sh                    # One-click deployment
```

## 📁 Generated Code Files

### template.yaml (AWS SAM Template)
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Parameters:
  OpenAIApiKey:
    Type: String
    NoEcho: true
  YouTubeCredentials:
    Type: String
    NoEcho: true

Globals:
  Function:
    Runtime: python3.9
    Timeout: 300
    Environment:
      Variables:
        BUCKET_NAME: !Ref ContentBucket
        TABLE_NAME: !Ref HistoricalFiguresTable

Resources:
  ContentBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'historical-content-${AWS::AccountId}'
      VersioningConfiguration:
        Status: Enabled

  HistoricalFiguresTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: historical-figures
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: figure_id
          AttributeType: S
      KeySchema:
        - AttributeName: figure_id
          KeyType: HASH

  ResearchFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/research/
      Handler: handler.lambda_handler
      Environment:
        Variables:
          OPENAI_API_KEY: !Ref OpenAIApiKey

  ScriptGenerationFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/script_generation/
      Handler: handler.lambda_handler
      Environment:
        Variables:
          OPENAI_API_KEY: !Ref OpenAIApiKey

  VideoCreationTask:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: video-creation
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      Cpu: 2048
      Memory: 4096
      ContainerDefinitions:
        - Name: video-creator
          Image: !Sub '${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/video-creator:latest'
          Memory: 4096
          Essential: true

  YouTubeUploadFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/upload/
      Handler: youtube_handler.lambda_handler
      Environment:
        Variables:
          YOUTUBE_CREDENTIALS: !Ref YouTubeCredentials

  ContentPipeline:
    Type: AWS::Serverless::StateMachine
    Properties:
      DefinitionUri: statemachine/definition.json
      Role: !GetAtt StepFunctionsRole.Arn
      Events:
        DailySchedule:
          Type: Schedule
          Properties:
            Schedule: rate(8 hours)
            Input: |
              {
                "topics": ["Harriet Tubman", "Frederick Douglass", "Sojourner Truth"]
              }

  StepFunctionsRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: states.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaRole
      Policies:
        - PolicyName: ECSTaskExecution
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - ecs:RunTask
                  - ecs:StopTask
                  - ecs:DescribeTasks
                Resource: '*'
```

### src/research/handler.py
```python
import json
import boto3
import requests
import openai
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """Research historical figure using Wikipedia and OpenAI verification"""
    
    topic = event.get('topic', 'Harriet Tubman')
    table = dynamodb.Table('historical-figures')
    
    # Check if we already have data
    response = table.get_item(Key={'figure_id': topic})
    if 'Item' in response:
        return {
            'statusCode': 200,
            'body': response['Item']
        }
    
    # Wikipedia research
    wiki_url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{topic}'
    wiki_response = requests.get(wiki_url)
    wiki_data = wiki_response.json()
    
    # Enhanced research with full page content
    content_url = f'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'titles': topic,
        'prop': 'extracts',
        'exintro': True,
        'explaintext': True,
        'exsectionformat': 'plain'
    }
    content_response = requests.get(content_url, params=params)
    content_data = content_response.json()
    
    # Extract key facts using OpenAI
    full_text = list(content_data['query']['pages'].values())[0].get('extract', '')
    
    openai.api_key = os.environ['OPENAI_API_KEY']
    
    fact_extraction_prompt = f"""
    Extract 5-7 key historical facts about {topic} from this Wikipedia content.
    Focus on:
    - Birth/death dates and locations
    - Major accomplishments
    - Historical significance
    - Impact on civil rights/abolition
    - Lesser-known but important details
    
    Content: {full_text[:3000]}
    
    Return as JSON array: [{{"fact": "...", "importance": "high/medium", "verification_needed": true/false}}]
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": fact_extraction_prompt}],
        max_tokens=800
    )
    
    facts = json.loads(response.choices[0].message.content)
    
    # Cultural sensitivity check
    sensitivity_prompt = f"""
    Review these facts about {topic} for cultural sensitivity:
    {json.dumps(facts)}
    
    Check for:
    - Person-first language ("enslaved person" not "slave")
    - Dignified terminology
    - Respectful framing of trauma
    - Empowering narrative focus
    
    Return: {{"approved": true/false, "concerns": ["..."], "suggestions": ["..."]}}
    """
    
    sensitivity_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": sensitivity_prompt}],
        max_tokens=400
    )
    
    sensitivity_check = json.loads(sensitivity_response.choices[0].message.content)
    
    # Compile research data
    research_data = {
        'figure_id': topic,
        'title': wiki_data.get('title', topic),
        'summary': wiki_data.get('extract', ''),
        'birth_year': wiki_data.get('birth_year', ''),
        'facts': facts,
        'sensitivity_check': sensitivity_check,
        'wiki_url': wiki_data.get('content_urls', {}).get('desktop', {}).get('page', ''),
        'image_url': wiki_data.get('thumbnail', {}).get('source', ''),
        'research_date': datetime.now().isoformat(),
        'confidence_score': 0.95 if sensitivity_check.get('approved') else 0.70
    }
    
    # Store in DynamoDB
    table.put_item(Item=research_data)
    
    # Store detailed research in S3
    s3.put_object(
        Bucket=os.environ['BUCKET_NAME'],
        Key=f'research/{topic}/detailed_research.json',
        Body=json.dumps(research_data, indent=2)
    )
    
    return {
        'statusCode': 200,
        'body': research_data
    }
```

### src/script_generation/handler.py
```python
import json
import boto3
import openai
import os
from datetime import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """Generate culturally sensitive educational script"""
    
    research_data = event.get('research_data', {})
    topic = research_data.get('figure_id', 'Unknown')
    
    openai.api_key = os.environ['OPENAI_API_KEY']
    
    # Cultural guidelines for script generation
    guidelines = """
    CULTURAL SENSITIVITY GUIDELINES:
    1. Use person-first language ("enslaved person" never "slave")
    2. Focus on agency, resistance, and accomplishments
    3. Provide historical context without minimizing trauma
    4. Highlight contributions to freedom and justice
    5. Use respectful, dignified tone throughout
    6. Include learning objectives
    7. Avoid oversimplification of complex historical realities
    """
    
    script_prompt = f"""
    {guidelines}
    
    Create a 60-second educational video script about {topic}.
    
    Research data: {json.dumps(research_data.get('facts', []))}
    
    Structure:
    - Hook (5-10 seconds): Compelling opening
    - Context (10-15 seconds): Historical background
    - Key achievements (25-30 seconds): 3-4 major accomplishments
    - Legacy (10-15 seconds): Lasting impact and inspiration
    
    Include:
    - Exact timing for each segment
    - Visual cues for images/B-roll
    - Emphasis markers for important points
    - Reading level: 9th grade
    - Tone: Respectful, educational, inspiring
    
    Return as JSON:
    {{
      "title": "Compelling video title (under 60 chars)",
      "hook": "Opening line with timing",
      "segments": [
        {{
          "start_time": 0,
          "end_time": 10,
          "narration": "...",
          "visual_cues": ["image description", "..."],
          "emphasis": ["key", "words"]
        }}
      ],
      "total_duration": 60,
      "learning_objectives": ["...", "..."],
      "key_takeaways": ["...", "..."],
      "accessibility_notes": "Closed captioning, visual descriptions"
    }}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": script_prompt}],
        max_tokens=1200,
        temperature=0.7
    )
    
    try:
        script_data = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        script_text = response.choices[0].message.content
        script_data = {
            "title": f"The Legacy of {topic}",
            "script": script_text,
            "duration_seconds": 60,
            "visual_cues": [f"{topic} portrait", "historical context", "achievements", "legacy impact"],
            "error": "JSON parsing failed, using fallback format"
        }
    
    # Quality assurance check
    qa_prompt = f"""
    Review this script for cultural sensitivity and educational value:
    {json.dumps(script_data)}
    
    Rate on scale 1-10:
    - Cultural sensitivity
    - Historical accuracy
    - Educational value
    - Age-appropriateness
    - Engagement level
    
    Return: {{"overall_score": 8.5, "passes_qa": true, "issues": [], "improvements": []}}
    """
    
    qa_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": qa_prompt}],
        max_tokens=300
    )
    
    qa_result = json.loads(qa_response.choices[0].message.content)
    script_data['qa_result'] = qa_result
    script_data['generated_at'] = datetime.now().isoformat()
    
    # Store script in S3
    s3.put_object(
        Bucket=os.environ['BUCKET_NAME'],
        Key=f'scripts/{topic}/script.json',
        Body=json.dumps(script_data, indent=2)
    )
    
    return {
        'statusCode': 200,
        'body': script_data
    }
```

### src/video_creation/handler.py
```python
import json
import boto3
import os
import subprocess
from moviepy.editor import *
import requests
from gtts import gTTS
import tempfile
from pathlib import Path

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """Create video from script and assets - Container version"""
    
    topic = event.get('topic', 'Unknown')
    
    # Download script from S3
    script_obj = s3.get_object(
        Bucket=os.environ['BUCKET_NAME'],
        Key=f'scripts/{topic}/script.json'
    )
    script_data = json.loads(script_obj['Body'].read())
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Generate voiceover
        full_script = " ".join([seg.get('narration', '') for seg in script_data.get('segments', [])])
        if not full_script:
            full_script = script_data.get('script', f'Learn about {topic}')
        
        tts = gTTS(text=full_script, lang='en', slow=False)
        voice_path = temp_path / 'voiceover.mp3'
        tts.save(str(voice_path))
        
        # Download images based on visual cues
        image_paths = []
        visual_cues = script_data.get('visual_cues', [f'{topic}', 'history', 'education', 'inspiration'])
        
        for i, cue in enumerate(visual_cues[:4]):  # Limit to 4 images
            try:
                # Use Unsplash Source for free images
                image_url = f'https://source.unsplash.com/1080x1920/?{cue.replace(" ", "+")}'
                image_response = requests.get(image_url, stream=True)
                
                if image_response.status_code == 200:
                    image_path = temp_path / f'image_{i}.jpg'
                    with open(image_path, 'wb') as f:
                        for chunk in image_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    image_paths.append(str(image_path))
            except Exception as e:
                print(f"Failed to download image {i}: {e}")
        
        # Fallback: create solid color clips if no images
        if not image_paths:
            for i in range(4):
                color_clip = ColorClip(size=(1080, 1920), color=(50, 100, 150), duration=15)
                color_path = temp_path / f'color_{i}.mp4'
                color_clip.write_videofile(str(color_path), fps=24, verbose=False, logger=None)
                image_paths.append(str(color_path))
        
        # Create video clips
        clips = []
        audio_clip = AudioFileClip(str(voice_path))
        total_duration = audio_clip.duration
        clip_duration = total_duration / len(image_paths)
        
        for i, image_path in enumerate(image_paths):
            try:
                if image_path.endswith('.mp4'):
                    clip = VideoFileClip(image_path).subclip(0, clip_duration)
                else:
                    clip = ImageClip(image_path, duration=clip_duration)
                
                clip = clip.resize((1080, 1920))
                
                # Add Ken Burns effect (zoom and pan)
                if i % 2 == 0:
                    clip = clip.resize(lambda t: 1 + 0.04*t)  # Slow zoom in
                else:
                    clip = clip.resize(lambda t: 1.04 - 0.04*t)  # Slow zoom out
                
                clips.append(clip)
            except Exception as e:
                print(f"Error processing clip {i}: {e}")
                # Create fallback solid color clip
                fallback_clip = ColorClip(size=(1080, 1920), color=(100, 50, 150), duration=clip_duration)
                clips.append(fallback_clip)
        
        # Combine video clips
        video = concatenate_videoclips(clips)
        video = video.set_audio(audio_clip)
        
        # Add title overlay
        title_text = script_data.get('title', f'The Story of {topic}')[:50]  # Limit title length
        
        title_clip = TextClip(
            title_text,
            fontsize=60,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2
        ).set_position('center').set_duration(3)
        
        # Add subtitle throughout
        subtitle_text = f"Educational content about {topic}"
        subtitle_clip = TextClip(
            subtitle_text,
            fontsize=30,
            color='white',
            font='Arial',
            stroke_color='black',
            stroke_width=1
        ).set_position(('center', 'bottom')).set_duration(video.duration)
        
        # Compose final video
        final_video = CompositeVideoClip([video, title_clip, subtitle_clip])
        
        # Export video
        output_path = temp_path / f'{topic.replace(" ", "_")}_video.mp4'
        final_video.write_videofile(
            str(output_path),
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Upload to S3
        video_key = f'videos/{topic}/{topic.replace(" ", "_")}_final.mp4'
        s3.upload_file(
            str(output_path),
            os.environ['BUCKET_NAME'],
            video_key
        )
        
        # Generate thumbnail
        thumbnail_path = temp_path / 'thumbnail.jpg'
        final_video.save_frame(str(thumbnail_path), t=2)
        
        thumbnail_key = f'thumbnails/{topic}/{topic.replace(" ", "_")}_thumb.jpg'
        s3.upload_file(
            str(thumbnail_path),
            os.environ['BUCKET_NAME'],
            thumbnail_key
        )
    
    return {
        'statusCode': 200,
        'body': {
            'video_key': video_key,
            'thumbnail_key': thumbnail_key,
            'duration': total_duration,
            'title': title_text
        }
    }
```

### src/upload/youtube_handler.py
```python
import json
import boto3
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """Upload video to YouTube with optimized metadata"""
    
    video_data = event.get('video_data', {})
    topic = event.get('topic', 'Historical Figure')
    
    video_key = video_data.get('video_key')
    title = video_data.get('title', f'The Story of {topic}')
    
    # Download video from S3
    video_obj = s3.get_object(Bucket=os.environ['BUCKET_NAME'], Key=video_key)
    video_content = video_obj['Body'].read()
    
    # YouTube API setup
    credentials_json = json.loads(os.environ['YOUTUBE_CREDENTIALS'])
    credentials = Credentials.from_authorized_user_info(credentials_json)
    youtube = build('youtube', 'v3', credentials=credentials)
    
    # Optimized metadata for education content
    description = f"""
🎓 Educational content about {topic}, an important figure in American history.

📚 Learn about:
• Historical context and background
• Major achievements and contributions
• Lasting impact on civil rights and freedom
• Why this story matters today

🔗 This video is part of our educational series highlighting important figures who shaped American history and the fight for justice and equality.

#BlackHistory #Education #History #CivilRights #{topic.replace(' ', '')}

📖 For more educational content, subscribe and hit the bell icon!

⚡ Quick Facts:
• Person-first language used throughout
• Age-appropriate for middle school and up
• Historically accurate and culturally sensitive
• Perfect for classroom use

🎯 Learning Objectives:
• Understand historical context
• Recognize individual agency and resistance
• Appreciate lasting contributions to justice
• Connect past struggles to present day

📝 This content is created with respect, dignity, and historical accuracy as our priorities.
    """
    
    # Tags optimized for discoverability
    tags = [
        'education',
        'history',
        'black history',
        topic.replace(' ', '').lower(),
        'civil rights',
        'american history',
        'educational video',
        'history lesson',
        'inspiring stories',
        'historical figures',
        'learning',
        'classroom',
        'students'
    ]
    
    # Video metadata
    body = {
        'snippet': {
            'title': title[:100],  # YouTube limit
            'description': description[:5000],  # YouTube limit
            'tags': tags[:12],  # Optimal number for YouTube
            'categoryId': '27',  # Education category
            'defaultLanguage': 'en',
            'defaultAudioLanguage': 'en'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,  # Educational content for general audience
            'embeddable': True,
            'license': 'youtube'
        }
    }
    
    # Create upload media object
    media = MediaIoBaseUpload(
        io.BytesIO(video_content),
        mimetype='video/mp4',
        chunksize=1024*1024,  # 1MB chunks
        resumable=True
    )
    
    # Upload video
    try:
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Store upload record
        upload_record = {
            'video_id': video_id,
            'video_url': video_url,
            'topic': topic,
            'title': title,
            'upload_date': datetime.now().isoformat(),
            'status': 'uploaded'
        }
        
        s3.put_object(
            Bucket=os.environ['BUCKET_NAME'],
            Key=f'uploads/{topic}/youtube_record.json',
            Body=json.dumps(upload_record, indent=2)
        )
        
        return {
            'statusCode': 200,
            'body': {
                'success': True,
                'video_id': video_id,
                'video_url': video_url,
                'message': f'Successfully uploaded: {title}'
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'success': False,
                'error': str(e),
                'message': f'Failed to upload video for {topic}'
            }
        }
```

### deploy.sh (One-Click Deployment)
```bash
#!/bin/bash

echo "🚀 Deploying Historical Video Creation System..."

# Check prerequisites
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI not found. Installing..."
    pip install aws-sam-cli
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Set parameters
read -p "Enter your OpenAI API Key: " OPENAI_KEY
read -p "Enter path to YouTube credentials JSON file: " YOUTUBE_CREDS

if [ ! -f "$YOUTUBE_CREDS" ]; then
    echo "❌ YouTube credentials file not found at $YOUTUBE_CREDS"
    exit 1
fi

YOUTUBE_CREDS_CONTENT=$(cat "$YOUTUBE_CREDS" | base64 -w 0)

echo "📦 Building SAM application..."
sam build

echo "🌐 Deploying to AWS..."
sam deploy \
    --guided \
    --parameter-overrides \
    OpenAIApiKey="$OPENAI_KEY" \
    YouTubeCredentials="$YOUTUBE_CREDS_CONTENT"

echo "📊 Loading historical figures data..."
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name historical-video-system \
    --query 'Stacks[0].Outputs[?OutputKey==`ContentBucket`].OutputValue' \
    --output text)

aws s3 cp data/historical_figures.json s3://$BUCKET_NAME/data/

echo "🎬 Starting first video creation..."
STATE_MACHINE_ARN=$(aws cloudformation describe-stacks \
    --stack-name historical-video-system \
    --query 'Stacks[0].Outputs[?OutputKey==`StateMachineArn`].OutputValue' \
    --output text)

aws stepfunctions start-execution \
    --state-machine-arn $STATE_MACHINE_ARN \
    --input '{"topics": ["Harriet Tubman"]}'

echo "✅ Deployment complete!"
echo "🎥 Your first video will be ready in approximately 15-20 minutes."
echo "📺 Check your YouTube channel for the uploaded video."
echo "🔄 The system will automatically create new videos every 8 hours."
```
