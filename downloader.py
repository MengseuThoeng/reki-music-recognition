"""
Media stream extraction service for Reki Music Recognition Bot.
Extracts audio streams from video links (TikTok, Reels, YouTube) for Shazam acoustic recognition.
Developer: @RekiReze
"""

import os
import re
import logging
import asyncio
import uuid
from typing import Optional
import yt_dlp

logger = logging.getLogger(__name__)

DOWNLOAD_DIR = os.path.abspath("downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


class MediaExtractor:
    def __init__(self, download_dir: str = DOWNLOAD_DIR):
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)

    async def extract_audio_from_link(self, url: str) -> Optional[str]:
        """
        Download only the first 15-20 seconds of audio from a video link (TikTok, Reels, Shorts).
        Used by the recognizer to fingerprint links.
        Returns: filepath to temporary audio snippet.
        """
        def _download():
            unique_id = uuid.uuid4().hex[:8]
            output_template = os.path.join(self.download_dir, f"link_{unique_id}.%(ext)s")

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '128',
                    }
                ],
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'max_filesize': 50 * 1024 * 1024,
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    logger.info(f"Extracting audio stream from URL: {url}")
                    info = ydl.extract_info(url, download=True)
                    if not info:
                        return None

                    expected_mp3 = os.path.splitext(ydl.prepare_filename(info))[0] + ".mp3"
                    if os.path.exists(expected_mp3):
                        return expected_mp3

                    for f in os.listdir(self.download_dir):
                        if unique_id in f and f.endswith(".mp3"):
                            return os.path.join(self.download_dir, f)

                    return None
            except Exception as e:
                logger.error(f"Failed to extract audio from URL {url}: {e}")
                return None

        return await asyncio.to_thread(_download)

    @staticmethod
    def cleanup_file(filepath: Optional[str]):
        """Safely remove a temporary file from disk."""
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {filepath}: {e}")
