# AI-Powered YouTube Shorts Generator

This is a highly modular, extensible AI-powered system that generates and uploads YouTube Shorts from user-provided images and context. 

## Features
- **LLM Scripting**: Uses Google Gemini to generate dynamic, short vertical video scripts.
- **Voice Clone/TTS**: High-quality text-to-speech using Microsoft Edge TTS natively.
- **Dynamic Shorts**: Automatic zoom/pan effects on static images.
- **Auto Subtitles**: Whisper-powered word-level timing for large, engaging captions.
- **YouTube API**: One-click OAuth uploads for seamless Shorts publishing.

## Architecture
The system uses **Dependency Injection (DI)** with abstract base classes (`src/core/interfaces.py`). Every provider (LLM, TTS, Video editing, Upload) is completely modular and replaceable without touching the core orchestration logic.

## Setup Instructions

### 1. Install System Requirements
Ensure you have `ffmpeg` installed for MoviePy and Whisper text-level transcriptions:
- **Windows**: Use winget or chocolatey (`winget install ffmpeg`) or download from https://www.gyan.dev/ffmpeg/builds/
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 2. Environment Setup
Create a virtual environment and install dependencies:
```bash
python -m venv .venv
# Activate on Windows: .\.venv\Scripts\activate
# Activate on Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### 3. API Keys & Configuration
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Fill in the `GEMINI_API_KEY` with your API key from Google AI Studio. 
*(Optional)* If you plan to upload to YouTube, get your OAuth `client_secrets.json` from Google Cloud Console and place it in the root folder.

### 4. Running the Application
```bash
python main.py --image "sample.jpg" --context "A motivational story about perseverance"
```

To automatically upload to YouTube (requires `client_secrets.json`):
```bash
python main.py --image "sample.jpg" --context "A motivational story about perseverance" --upload
```
