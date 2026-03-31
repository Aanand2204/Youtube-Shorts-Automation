import os
import math
import warnings
import numpy as np
from PIL import Image
from typing import List, Dict

try:
    # MoviePy 1.x API
    from moviepy.editor import (
        AudioFileClip, ImageClip, TextClip, CompositeVideoClip, VideoClip
    )
    MOVIEPY_V2 = False
except ModuleNotFoundError:
    # MoviePy 2.x API
    from moviepy import (
        AudioFileClip, ImageClip, TextClip, CompositeVideoClip, VideoClip
    )
    MOVIEPY_V2 = True

from src.core.interfaces import IVideoGenerator
from src.utils.logger import get_logger

logger = get_logger(__name__)
warnings.filterwarnings("ignore")

class MoviePyProvider(IVideoGenerator):
    def __init__(self, target_resolution=(1080, 1920)):
        self.resolution = target_resolution

    def _generate_subtitles(self, audio_path: str) -> List[Dict]:
        logger.info("Loading pre-calculated word timings from Edge TTS...")
        json_path = audio_path.replace(".wav", ".json")
        try:
            import json
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load precise subtitles: {e}")
            return []

    def _create_subtitle_clips(self, words: List[Dict], video_size: tuple) -> List[VideoClip]:
        subtitle_clips = []
        # Group words into chunks (e.g., 2-3 words per screen)
        chunk_size = 3
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i + chunk_size]
            text = " ".join([w["text"] for w in chunk])
            start_time = chunk[0]["start"]
            end_time = chunk[-1]["end"]
            
            # TextClip syntax changed in V2
            if MOVIEPY_V2:
                txt_clip = TextClip(
                    text=text, 
                    font_size=75, 
                    color='white', 
                    stroke_color='black', 
                    stroke_width=3, 
                    font='Impact',
                    method='caption',
                    size=(int(video_size[0] * 0.9), None),
                    horizontal_align='center'
                )
                txt_clip = txt_clip.with_position(('center', 'center')).with_start(start_time).with_end(end_time)
            else:
                txt_clip = TextClip(
                    text, 
                    fontsize=75, 
                    color='white', 
                    stroke_color='black', 
                    stroke_width=3, 
                    font='Impact',
                    method='caption',
                    size=(int(video_size[0] * 0.9), None),
                    align='center'
                )
                txt_clip = txt_clip.set_position(('center', 'center')).set_start(start_time).set_end(end_time)
                
            subtitle_clips.append(txt_clip)
        
        return subtitle_clips

    def _apply_zoom(self, clip: ImageClip, zoom_ratio=0.04) -> VideoClip:
        """Applies a slow zoom-in effect to an ImageClip"""
        def effect(get_frame, t):
            img = Image.fromarray(get_frame(t))
            base_size = img.size
            new_size = [
                int(base_size[0] * (1 + (zoom_ratio * t))),
                int(base_size[1] * (1 + (zoom_ratio * t)))
            ]
            x1 = (new_size[0] - base_size[0]) // 2
            y1 = (new_size[1] - base_size[1]) // 2
            
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            img = img.crop((x1, y1, x1 + base_size[0], y1 + base_size[1]))
            return np.array(img)
        
        # fl is renamed to transform in V2
        if MOVIEPY_V2:
            return clip.transform(effect)
        else:
            return clip.fl(effect)

    def generate_video(self, image_path: str, audio_path: str, output_path: str) -> str:
        logger.info(f"Starting video generation: image={image_path}, audio={audio_path}")
        
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        logger.info(f"Video duration will be set to audio duration: {duration}s")
        
        img = Image.open(image_path)
        target_ratio = self.resolution[0] / self.resolution[1]
        img_ratio = img.width / img.height
        
        if img_ratio > target_ratio:
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))
            
        img = img.resize(self.resolution, Image.Resampling.LANCZOS)
        temp_img_path = "temp_resized_base.png"
        img.save(temp_img_path)
        
        if MOVIEPY_V2:
            base_clip = ImageClip(temp_img_path).with_duration(duration)
        else:
            base_clip = ImageClip(temp_img_path).set_duration(duration)
            
        logger.info("Applying dynamic zoom-in effect...")
        base_clip = self._apply_zoom(base_clip, zoom_ratio=0.03)
        
        words = self._generate_subtitles(audio_path)
        subtitle_clips = self._create_subtitle_clips(words, self.resolution)
        
        logger.info("Compositing layers together...")
        final_video = CompositeVideoClip([base_clip] + subtitle_clips)
        
        if MOVIEPY_V2:
            final_video = final_video.with_audio(audio_clip)
        else:
            final_video = final_video.set_audio(audio_clip)
            
        logger.info(f"Writing final video to {output_path}...")
        final_video.write_videofile(
            output_path, 
            fps=30, 
            codec="libx264", 
            audio_codec="aac",
            preset="ultrafast",
            logger=None
        )
        
        # Cleanup
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
            
        logger.info("Video generation completed.")
        return output_path
