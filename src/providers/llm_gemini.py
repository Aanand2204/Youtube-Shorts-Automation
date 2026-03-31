import os
import json
from google import genai
from google.genai import types
from PIL import Image
from typing import Dict
from src.core.interfaces import IScriptGenerator, IMetadataGenerator
from src.utils.logger import get_logger
from src.utils.config import Config

logger = get_logger(__name__)

class GeminiProvider(IScriptGenerator, IMetadataGenerator):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)

    def generate_script(self, image_path: str, context: str, language: str = "English") -> str:
        logger.info(f"Generating script for image: {image_path} with context: {context} in language: {language}")
        
        try:
            image = Image.open(image_path)
            
            prompt = f"""
You are an expert short-form video scriptwriter (YouTube Shorts / TikTok). 
Analyze the provided image and the context given below.
Write a highly engaging, emotional, or captivating script to be narrated over this image.
The narration speed will be conversational.
The script MUST be written strictly in the {language} language.
The total script length must be EXACTLY between 40 and 60 words (appx 15 seconds).
DO NOT include visual directions or sound directions (like [Music fades in] or [Upbeat tone]).
Provide ONLY the spoken text in {language}.

Context: {context}
"""
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[image, prompt]
            )
            script = response.text.strip()
            logger.info(f"Generated script ({len(script.split())} words)")
            return script
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            raise

    def generate_metadata(self, script: str, context: str) -> Dict[str, str]:
        logger.info("Generating video metadata...")
        
        prompt = f"""
You are an expert YouTube SEO specialist.
Based on the following short video script and the provided context, generate the metadata for a YouTube Short video.
The response must be valid JSON matching this schema:
{{
    "title": "A catchy title under 60 characters with an emoji",
    "description": "A 2-3 sentence engaging description including relevant keywords",
    "tags": "comma, separated, list, of, 5-10, tags"
}}

Context: {context}
Script: {script}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            metadata = json.loads(response.text)
            logger.info("Generated metadata successfully.")
            return metadata
        except Exception as e:
            logger.error(f"Error generating metadata: {e}")
            # Fallback
            return {
                "title": f"Shorts via AI ({context[:20]})",
                "description": f"Generated video for context: {context}\n\n#shorts",
                "tags": "shorts,ai,video"
            }
