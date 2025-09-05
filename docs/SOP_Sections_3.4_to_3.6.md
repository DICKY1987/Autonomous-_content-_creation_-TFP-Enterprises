# SOP — Sections 3.4 to 3.6
**Title:** Agentic AI Work Instructions for Video Assembly → QA → Upload  
**Scope:** Implements §§3.4–3.6 of the Autonomous AI YouTube Content Business Plan  
**Version:** 1.0  
**Traceability:** Each step uses stable hierarchical numbering for machine targeting (e.g., `3.4.1.2`).

---

## 0. Folder Layout & Artifacts
```
project_root/
├─ audio/
│  ├─ voiceover.wav
│  └─ music_bed.wav
├─ brand/
│  ├─ intro.mp4
│  ├─ outro.mp4
│  ├─ logo.png
│  ├─ Inter-Regular.ttf
│  ├─ Inter-Bold.ttf
│  └─ theme.json
├─ captions/
│  └─ captions.srt
├─ media/
│  ├─ scene1.jpg
│  ├─ scene2.mp4
│  └─ ...
├─ manifests/
│  ├─ timeline.json
│  └─ assets.json
├─ qa/
│  ├─ facts_report.json
│  ├─ tech_report.json
│  └─ license_report.json
├─ logs/{trace_id}/
├─ alerts/
│  └─ review_bundle.zip
├─ script/
│  └─ script.txt
└─ build/
   ├─ main_nobrands.mp4
   ├─ main_burnin.mp4
   ├─ with_intro.mp4
   ├─ with_intro_outro.mp4
   ├─ branded.mp4
   └─ final_short.mp4
```

---

## 3.4 Video Assembly — Work Instructions

### 3.4.1 Rendering Pipeline (FFmpeg/MoviePy + Auto-Captioning)

#### 3.4.1.1 Inputs (required artifacts)
- `audio/voiceover.wav` — mono, 48 kHz
- `audio/music_bed.wav` — stereo, 48 kHz
- `media/` — cleared images/clips
- `script/script.txt` — final, sentence-segmented
- `brand/` — logo PNG (alpha), fonts, intro/outro
- `manifests/timeline.json` — timing plan

**`manifests/timeline.json` (schema):**
```json
{
  "fps": 30,
  "canvas": {"w": 1080, "h": 1920},
  "music_gain_db": -20,
  "clips": [
    {
      "type": "image",
      "src": "media/scene1.jpg",
      "start": 0.00,
      "dur": 3.50,
      "ken_burns": {"zoom": 1.08, "pan": "tl->br"}
    }
  ],
  "captions": [
    {"text": "Sentence 1.", "start": 0.00, "end": 2.60},
    {"text": "Sentence 2.", "start": 2.60, "end": 5.40}
  ]
}
```

#### 3.4.1.2 Audio prep (normalize & mix)
```bash
# Normalize VO to -16 LUFS
ffmpeg -i audio/voiceover.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 audio/voiceover_norm.wav

# Normalize music to -23 LUFS
ffmpeg -i audio/music_bed.wav -af loudnorm=I=-23:TP=-1.5:LRA=11 audio/music_norm.wav

# Optional: sidechain ducking (music ducked by VO)
ffmpeg -i audio/voiceover_norm.wav -i audio/music_norm.wav \
  -filter_complex "[1:a][0:a]sidechaincompress=threshold=0.03:ratio=8:attack=5:release=200[out]" \
  -map "[out]" -c:a pcm_s16le audio/mix.wav
```

#### 3.4.1.3 Auto-captions
- **Path A:** Use script timings (preferred if TTS provides word/phoneme times) → build `captions/captions.srt`.
- **Path B:** ASR on mixed audio (Whisper example):
```bash
whisper audio/mix.wav --language en --task transcribe --model base --srt --output_dir captions/
```

#### 3.4.1.4 Visual assembly (MoviePy reference)
```python
# file: tools/render.py
from moviepy.editor import *
import json

plan = json.load(open("manifests/timeline.json"))
W,H,fps = plan["canvas"]["w"], plan["canvas"]["h"], plan["fps"]

layers = []
for c in plan["clips"]:
    if c["type"] == "image":
        clip = (ImageClip(c["src"]).set_duration(c["dur"]).resize((W,H)))
        if "ken_burns" in c:
            clip = clip.fx(vfx.zoom_in, final_scale=c["ken_burns"]["zoom"])
    else:
        clip = (VideoFileClip(c["src"]).without_audio().resize((W,H)).set_duration(c["dur"]))
    layers.append(clip.set_start(c["start"]))

video = CompositeVideoClip(layers, size=(W,H))
vo = AudioFileClip("audio/voiceover_norm.wav")
music = AudioFileClip("audio/music_norm.wav").volumex(10**(plan["music_gain_db"]/20.0))
audio_mix = CompositeAudioClip([music, vo])
video = video.set_audio(audio_mix).set_fps(fps)

video.write_videofile("build/main_nobrands.mp4", codec="libx264", audio_codec="aac", bitrate="8M", threads=4)
```

#### 3.4.1.5 Caption burn-in (optional; sidecar preferred)
```bash
ffmpeg -i build/main_nobrands.mp4 \
  -vf "subtitles=captions/captions.srt:force_style='Fontsize=28,PrimaryColour=&H00FFFFFF&'" \
  -c:a copy build/main_burnin.mp4
```

#### 3.4.1.6 Auto-acceptance checks
- Length ≤ 60.0 s, fps = 30, geometry = 1080×1920, 1:1 PAR
- Audio peak < -1.0 dBTP; integrated loudness ≈ -14 to -16 LUFS
- No black/freeze frames > 1 s
- Captions present (sidecar or burn-in)

---

### 3.4.2 Branding Modules (Intro/Outro, Lower-thirds)

#### 3.4.2.1 Theme file
`brand/theme.json`
```json
{
  "primary_color": "#00E5FF",
  "accent_color": "#111827",
  "font_regular": "Inter-Regular.ttf",
  "font_bold": "Inter-Bold.ttf",
  "logo": "brand/logo.png",
  "cta_text": "Subscribe for more!",
  "watermark_opacity": 0.10
}
```

#### 3.4.2.2 Intro overlay (1–1.5 s)
```bash
ffmpeg -i build/main_nobrands.mp4 -i brand/intro.mp4 \
  -filter_complex "[1:v]scale=1080:1920[intro];[intro][0:v]xfade=transition=fade:duration=0.5:offset=0[intromix]" \
  -map "[intromix]" -map 0:a -c:v libx264 -c:a aac -shortest build/with_intro.mp4
```

#### 3.4.2.3 Outro end-card (1.5–2.0 s)
```bash
ffmpeg -i build/with_intro.mp4 -i brand/outro.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=END-2.0[out]" \
  -map "[out]" -map 0:a -c:v libx264 -c:a aac build/with_intro_outro.mp4
```

#### 3.4.2.4 Watermark
```bash
ffmpeg -i build/with_intro_outro.mp4 -i brand/logo.png \
  -filter_complex "[1]format=rgba,colorchannelmixer=aa=0.10[wm];[0][wm]overlay=W-w-36:36:format=auto" \
  -c:a copy build/branded.mp4
```

#### 3.4.2.5 Lower-thirds (MoviePy)
```python
# file: tools/lower_third.py
from moviepy.editor import *

base = VideoFileClip("build/branded.mp4")
lt = (TextClip("@YourChannel", fontsize=54, font="Inter-Bold", color="white", bg_color="#111827")
      .set_position(("center", 1400)).set_duration(2.0).set_start(0.8))
final = CompositeVideoClip([base, lt])
final.write_videofile("build/final_branded.mp4", codec="libx264", audio_codec="aac", bitrate="8M")
```

---

### 3.4.3 Output Specifications (YouTube Shorts)
- **Resolution:** 1080×1920 (9:16)
- **FPS:** 30
- **Codec:** H.264 High@4.2, yuv420p
- **Bitrate:** 6–10 Mbps (CRF 18–21 or CBR 8 Mbps)
- **Audio:** AAC LC, 128–192 kbps, 48 kHz
- **Max length:** ≤ 60 s
- **Captions:** Prefer sidecar `.srt`

**Reference encode:**
```bash
ffmpeg -i build/final_branded.mp4 -c:v libx264 -pix_fmt yuv420p -profile:v high -level 4.2 \
 -r 30 -b:v 8M -maxrate 8M -bufsize 16M -c:a aac -b:a 160k build/final_short.mp4
```

---

## 3.5 Pre-Publish QA — Work Instructions

### 3.5.1 Fact verification
1. Extract sentence claims from `script/script.txt`.
2. Retrieve 2–3 independent sources per claim.
3. Score each claim: evidence count, source authority, semantic agreement (0–1).
4. Gate: average confidence ≥ 0.90, no claim < 0.70.
5. Emit `qa/facts_report.json`; on fail, create `alerts/HITL_factcheck.md` and halt.

**`qa/facts_report.json` example:**
```json
{
  "avg_conf": 0.93,
  "claims":[
    {"text":"X happened in 1969.","confidence":0.96,"sources":["https://...","https://..."]}
  ]
}
```

### 3.5.2 Technical compliance checks
- Duration 1–60 s; 1080×1920; fps=30; SAR 1:1
- Audio: max peak < -1.0 dBTP; LUFS -14±2
- No black/freeze frames > 1 s
- Captions present

**Probe:**
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of json build/final_short.mp4
ffmpeg -i build/final_short.mp4 -filter_complex "blackdetect=d=1:pix_th=0.10" -f null -
```
**Emit:** `qa/tech_report.json` with `status: pass|fail`.

### 3.5.3 Copyright safety scan
- `manifests/assets.json` lists every asset with license, URL, proof, checksum.
- Reject missing/ambiguous licenses; flag restricted sources.
- Emit `qa/license_report.json`; on fail → HITL.

**`manifests/assets.json` (schema):**
```json
{
  "assets":[
    {"path":"media/scene1.jpg","source_url":"https://...","license":"CC0","proof":"link_or_receipt","sha256":"..."},
    {"path":"audio/music_bed.wav","source_url":"https://...","license":"royalty_free","proof":"invoice_123.pdf","sha256":"..."}
  ]
}
```

### 3.5.4 Human-in-the-loop alert (< 90% confidence)
- Trigger when any `*_report.status == "fail"` or `facts.avg_conf < 0.90`.
- Bundle `alerts/review_bundle.zip` (video + reports).
- Notify (email/Slack) with Approve/Reject/Fix links.
- On Approve → proceed to 3.6; on Reject → stop and open issue.

---

## 3.6 Upload & Metadata Optimization — Work Instructions

### 3.6.1 Metadata generation (titles, descriptions, tags)
- Title ≤ 60 chars; two variants (`title_A`, `title_B`).
- Description 2–3 lines + 3–5 hashtags (incl. `#shorts`).
- Tags 10–15 (primary, secondary, related).
- Emit `metadata.json`:
```json
{
  "title_A":"5 facts about X you didn’t know",
  "title_B":"X in 30 seconds: the surprising part",
  "description":"Quick facts about X. Learn something new in 30s! #shorts #X #education",
  "tags":["X","X facts","shorts","education","learning","fast facts"],
  "categoryId":"27",
  "publishAt":"2025-09-01T15:00:00Z"
}
```

### 3.6.2 Thumbnails (A/B)
- Two variants: `thumbs/thumb_A.png`, `thumbs/thumb_B.png`
- ≤ 4 words, big text, brand colors, safe margins

### 3.6.3 Upload & schedule (YouTube API)
```python
# file: tools/upload.py
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json

creds = ...  # OAuth2 creds
meta = json.load(open("metadata.json"))
youtube = build("youtube","v3", credentials=creds)

media = MediaFileUpload("build/final_short.mp4", mimetype="video/mp4", resumable=True)

body = {
  "snippet": {
    "title": meta["title_A"],
    "description": meta["description"],
    "tags": meta["tags"],
    "categoryId": meta.get("categoryId","27")
  },
  "status": {
    "privacyStatus":"private",
    "selfDeclaredMadeForKids": False,
    "publishAt": meta["publishAt"]
  }
}
resp = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
video_id = resp["id"]

# Set thumbnail A
youtube.thumbnails().set(videoId=video_id, media_body="thumbs/thumb_A.png").execute()

# Upload captions
youtube.captions().insert(part="snippet", body={
  "snippet":{"videoId":video_id,"language":"en","name":"English","isDraft":False}
}, media_body="captions/captions.srt").execute()
```

### 3.6.4 Shadow A/B rotation (early impressions)
```python
# After ~2 hours, switch to B and track CTR deltas
youtube.videos().update(part="snippet", body={
  "id": video_id,
  "snippet": {"title": meta["title_B"], "description": meta["description"], "categoryId": meta.get("categoryId","27")}
}).execute()
youtube.thumbnails().set(videoId=video_id, media_body="thumbs/thumb_B.png").execute()
```

### 3.6.5 Post-publish checks
- Verify public status at `publishAt`.
- Pull metrics 1h/6h/24h: impressions, CTR, avg view, retention@3s/10s/complete.
- If under thresholds (e.g., CTR < 4%, retention@10s < 40%): set winning A/B, refresh description first line.

---

## 3.6.6 Idempotency & Logging
- **Trace ID:** `YYYYMMDD-topic-hash`
- **Logs:** `logs/{trace_id}/{step}.json` → `{status, duration_ms, errors}`
- **Artifact checksums:** skip step if inputs unchanged; else version `_v2`

---

## 3.6.7 Go/No-Go Gates
- GO only if:
  - `qa/tech_report.status == "pass"`
  - `qa/license_report.status == "pass"`
  - `qa/facts_report.avg_conf >= 0.90`
- Else: HITL and halt.
