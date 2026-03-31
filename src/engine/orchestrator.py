import os
import asyncio
from src.core.interfaces import (
    IScriptGenerator, 
    IVoiceGenerator, 
    IVideoGenerator, 
    IMetadataGenerator, 
    IUploader
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ShortsGeneratorEngine:
    def __init__(
        self,
        script_gen: IScriptGenerator,
        voice_gen: IVoiceGenerator,
        video_gen: IVideoGenerator,
        metadata_gen: IMetadataGenerator,
        uploader: IUploader
    ):
        self.script_gen = script_gen
        self.voice_gen = voice_gen
        self.video_gen = video_gen
        self.metadata_gen = metadata_gen
        self.uploader = uploader

    async def generate_assets(self, image_path: str, context: str, language: str = "English", ui_progress_hook=None):
        def report(progress_val, msg):
            logger.info(msg)
            if ui_progress_hook:
                ui_progress_hook(progress_val, msg)

        try:
            report(0.0, f"Starting Shorts pipeline for: {image_path} | Context: {context} | Language: {language}")
            
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            audio_path = os.path.join(output_dir, "temp_voice.wav")
            video_path = os.path.join(output_dir, "final_short.mp4")
            
            # 1. Script Generation
            report(0.1, f"Step 1/4: Analyzing image and Synthesizing {language} script via AI...")
            script = self.script_gen.generate_script(image_path, context, language)
            logger.info(f"--- GENERATED SCRIPT ---\n{script}\n------------------------")
            
            # 2. Metadata Generation
            report(0.3, "Step 2/4: Generating optimized YouTube metadata...")
            metadata = self.metadata_gen.generate_metadata(script, context)
            logger.info(f"--- GENERATED METADATA ---\nTitle: {metadata.get('title')}\nDesc: {metadata.get('description')}\nTags: {metadata.get('tags')}\n--------------------------")
            
            # 3. Voice Generation (Async)
            report(0.5, "Step 3/4: Synthesizing voice narrative from script...")
            await self.voice_gen.generate_voice(script, audio_path, language)
            
            # 4. Video Generation
            report(0.7, "Step 4/4: Applying dynamic zoom effects and compositing subtitles...")
            self.video_gen.generate_video(image_path, audio_path, video_path)
            
            report(1.0, f"Done! Video perfectly rendered and saved.")

            
            return {
                "script": script,
                "metadata": metadata,
                "audio_path": audio_path,
                "video_path": video_path
            }
        except Exception as e:
            logger.exception("Pipeline failed with trace:")
            raise

    def upload_to_youtube(self, video_path: str, metadata: dict) -> str:
        logger.info("Proceeding to YouTube Upload...")
        url = self.uploader.upload_video(video_path, metadata)
        logger.info(f"Successfully uploaded! Video URL: {url}")
        return url

    async def generate_short(self, image_path: str, context: str, auto_upload: bool = False, language: str = "English"):
        """Original unified flow for CLI compatibility."""
        assets = await self.generate_assets(image_path, context, language)
        if auto_upload:
            self.upload_to_youtube(assets["video_path"], assets["metadata"])
        else:
            logger.info("Auto-upload disabled. Please review the output folder.")
            return assets["video_path"], assets["metadata"]
