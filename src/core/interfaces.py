from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple

class IScriptGenerator(ABC):
    @abstractmethod
    def generate_script(self, image_path: str, context: str, language: str = "English") -> str:
        """
        Takes an image and context, returns a short script suitable for ~15 seconds in the specified language.
        """
        pass

class IVoiceGenerator(ABC):
    @abstractmethod
    async def generate_voice(self, script: str, output_path: str, language: str = "English") -> str:
        """
        Takes a generated script, outputs to an MP3/WAV file, and returns the file path.
        """
        pass

class IVideoGenerator(ABC):
    @abstractmethod
    def generate_video(self, image_path: str, audio_path: str, output_path: str) -> str:
        """
        Creates a vertical video combining the original image (with zooming effect),
        the generated audio, and generated subtitles. Returns output file path.
        """
        pass

class IMetadataGenerator(ABC):
    @abstractmethod
    def generate_metadata(self, script: str, context: str) -> Dict[str, str]:
        """
        Generates YouTube metadata from the script and context.
        Returns a dictionary with 'title', 'description', and 'tags'.
        """
        pass

class IUploader(ABC):
    @abstractmethod
    def upload_video(self, video_path: str, metadata: Dict[str, str], visibility: str = "private") -> str:
        """
        Uploads the given video with the provided metadata to YouTube (or fallback destination).
        Returns the video URL or Video ID.
        """
        pass
