import os
import uuid
import asyncio
from fastapi import FastAPI, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import aiofiles

from main import build_engine
from src.utils.logger import get_logger

logger = get_logger("server")

app = FastAPI(title="AI Shorts Generator")

# Initialize Engine
engine = build_engine()

# Temporary store for upload data to bridge POST and WebSocket
UPLOAD_CACHE = {}

# Ensure directories exist
os.makedirs("output/uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files and output files so browser can render them
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")

@app.post("/api/upload_context")
async def upload_context(
    image: UploadFile = File(...),
    context: str = Form(...),
    language: str = Form(...)
):
    """
    Step 1: Save the incoming image and context parameters, return a UUID.
    """
    task_id = str(uuid.uuid4())
    ext = os.path.splitext(image.filename)[1] or ".jpg"
    image_path = os.path.join("output", "uploads", f"{task_id}{ext}")
    
    # Save uploaded file asynchronously
    async with aiofiles.open(image_path, 'wb') as out_file:
        content = await image.read()
        await out_file.write(content)
        
    # Store parameters in memory for the websocket to pick up
    UPLOAD_CACHE[task_id] = {
        "image_path": image_path,
        "context": context,
        "language": language
    }
    
    return {"task_id": task_id}

@app.websocket("/api/ws/generate/{task_id}")
async def websocket_generate(websocket: WebSocket, task_id: str):
    """
    Step 2: Start the generation pipeline, piping progress logs directly to the WebSocket.
    """
    await websocket.accept()
    
    if task_id not in UPLOAD_CACHE:
        await websocket.send_json({"error": "Invalid Task ID. Please upload context first."})
        await websocket.close()
        return
        
    task_data = UPLOAD_CACHE.pop(task_id)
    image_path = task_data["image_path"]
    context = task_data["context"]
    language = task_data["language"]
    
    def ui_progress_hook(val, msg):
        # We spawn a background async task to send the websocket JSON because the hook inside orchestrator is synchronous.
        # This safely hooks into the running async event loop.
        asyncio.create_task(websocket.send_json({"progress": val, "message": msg}))
        
    try:
        # Give UI a moment to connect visually
        await asyncio.sleep(0.5)
        
        # Fire pipeline natively
        assets = await engine.generate_assets(
            image_path=image_path,
            context=context,
            language=language,
            ui_progress_hook=ui_progress_hook
        )
        
        # We need the final client-facing path for the video. "output/final_short.mp4" mounts to "/output/final_short.mp4"
        # However, to avoid caching issues on frontend, append a timestamp
        import time
        video_url = f"/output/final_short.mp4?t={int(time.time())}"
        
        # Push Final Success
        await websocket.send_json({"progress": 1.0, "message": "Video generation completed successfully!", "assets": {
            "video_url": video_url,
            "script": assets["script"],
            "title": assets["metadata"].get("title", ""),
            "description": assets["metadata"].get("description", ""),
            "tags": assets["metadata"].get("tags", "")
        }})
        
    except Exception as e:
        logger.exception("Pipeline failed in web generation:")
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()

@app.post("/api/upload_youtube")
async def upload_youtube(
    title: str = Form(...),
    description: str = Form(...),
    tags: str = Form(...)
):
    """
    Step 3: Auto-upload the cached final video to YouTube via Data API.
    """
    video_path = "output/final_short.mp4"
    if not os.path.exists(video_path):
        return JSONResponse(status_code=400, content={"error": "No generated video found."})
        
    metadata = {
        "title": title,
        "description": description,
        "tags": tags
    }
    
    try:
        url = engine.upload_to_youtube(video_path, metadata)
        return {"url": url}
    except Exception as e:
        logger.error(f"YouTube Upload Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Catch-all to serve index.html
@app.get("/")
async def serve_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=f.read())
