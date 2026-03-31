import os
from typing import Dict
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.core.interfaces import IUploader
from src.utils.logger import get_logger
from src.utils.config import Config

logger = get_logger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

class YouTubeAPIProvider(IUploader):
    def __init__(self):
        self.client_secrets_file = Config.YOUTUBE_CLIENT_SECRETS_FILE
        self.youtube = None

    def _authenticate(self):
        if not os.path.exists(self.client_secrets_file):
            logger.error(f"Missing {self.client_secrets_file}. Cannot upload to YouTube via API.")
            raise FileNotFoundError(f"OAuth credentials expected at: {self.client_secrets_file}")
            
        logger.info("Authenticating with YouTube API...")
        # A full production system would cache the credentials in token.json
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, SCOPES)
        credentials = flow.run_local_server(port=0)
        self.youtube = build("youtube", "v3", credentials=credentials)

    def upload_video(self, video_path: str, metadata: Dict[str, str], visibility: str = "private") -> str:
        if not self.youtube:
            self._authenticate()
            
        logger.info(f"Uploading {video_path} to YouTube as {visibility}...")
        try:
            body = {
                "snippet": {
                    "title": metadata.get("title", "AI YouTube Short"),
                    "description": metadata.get("description", "Uploaded by AI."),
                    "tags": metadata.get("tags", "").split(","),
                    "categoryId": "22" # 22 is usually "People & Blogs"
                },
                "status": {
                    "privacyStatus": visibility,
                    "selfDeclaredMadeForKids": False
                }
            }
            
            # 10485760 is 10 MB chunk size
            media = MediaFileUpload(video_path, chunksize=10485760, resumable=True)
            
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload Progress: {int(status.progress() * 100)}%")
            
            video_id = response.get("id")
            logger.info(f"Upload complete! Video ID: {video_id}")
            return f"https://youtube.com/shorts/{video_id}"
            
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            raise
