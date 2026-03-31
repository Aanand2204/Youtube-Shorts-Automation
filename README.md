# AI-Powered YouTube Shorts Generator

A highly modular, extensible AI-powered web and CLI application that generates and automatically uploads YouTube Shorts from user-provided images and context.

## 🚀 Features

- **Web Interface**: A sleek, bespoke vanilla JavaScript (ES Module) and HTML/CSS web app powered by **FastAPI**. Includes real-time WebSocket progress streaming.
- **LLM Scripting**: Uses Google GenAI (Gemini) to generate dynamic, vertical video scripts perfectly timed for 15-60 second Shorts.
- **Voice Synthesis**: High-quality text-to-speech using Microsoft Edge TTS natively.
- **Dynamic Video Compositing**: Automatic kinetic zoom/pan effects on static images using MoviePy.
- **Auto Subtitles**: OpenAI Whisper-powered word-level timing for large, engaging, TikTok/Shorts-style captions.
- **YouTube API Integration**: One-click OAuth uploads for seamless Shorts publishing directly from the web interface or CLI.

## 🏗️ Architecture

The system is built on a robust, decoupled architecture using **Dependency Injection (DI)** with abstract base classes (`src/core/interfaces.py`). Every provider (LLM, TTS, Video editing, YouTube Upload) is completely modular and replaceable without touching the core orchestration logic. The web frontend communicates with the `FastAPI` backend to pipe progress asynchronously.

## 🛠️ Setup Instructions

### 1. Install System Requirements
Ensure you have `ffmpeg` installed for MoviePy and Whisper text-level transcriptions:
- **Windows**: Use winget or chocolatey (`winget install ffmpeg`) or download from https://www.gyan.dev/ffmpeg/builds/
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 2. Environment Setup
Create a virtual environment and install dependencies:
```bash
python -m venv .venv

# Activate on Windows: 
.\.venv\Scripts\activate

# Activate on Mac/Linux: 
source .venv/bin/activate
```
Install Python requirements:
```bash
pip install -r requirements.txt
```

### 3. API Keys & Configuration
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Fill in the `GEMINI_API_KEY` with your API key from Google AI Studio. 

*(Optional)* If you plan to use the auto-upload feature to publish to YouTube, you must download your OAuth `client_secrets.json` from the Google Cloud Console and place it in the `credentials/` folder.

## 💻 Running the Application

### Method A: Web Interface (Recommended)
Launch the FastAPI server to access the GUI in your browser.
```bash
uvicorn src.server:app --reload
```
Once running, open your browser and navigate to `http://127.0.0.1:8000`.

### Method B: Command Line Interface (CLI)
You can completely bypass the UI and generate shorts directly from your terminal:
```bash
python main.py --image "sample.jpg" --context "A motivational story about perseverance" --language "English"
```

To automatically upload to YouTube via the CLI (requires `credentials/client_secrets.json`):
```bash
python main.py --image "sample.jpg" --context "A motivational story about perseverance" --upload
```
