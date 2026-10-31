"""
Music recognition service for Reki Music Recognition Bot.
Uses ShazamIO for acoustic fingerprinting and ffmpeg for audio snippet extraction.
Developer: @RekiReze
"""

import os
import logging
import asyncio
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from shazamio import Shazam

logger = logging.getLogger(__name__)


@dataclass
class TrackInfo:
    track_id: str
    title: str
    artist: str
    album: str = "Single"
    genre: str = "Music"
    release_year: str = ""
    cover_url: Optional[str] = None
    shazam_url: Optional[str] = None
    apple_music_url: Optional[str] = None
    youtube_url: Optional[str] = None
    spotify_url: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def search_query(self) -> str:
        """Query string for streaming lookups."""
        if self.artist and self.artist.lower() not in self.title.lower():
            return f"{self.artist} - {self.title}"
        return self.title

    def format_links_html(self) -> str:
        """Format streaming service links into clean HTML bullet points."""
        links: List[str] = []
        if self.youtube_url:
            links.append(f'• <a href="{self.youtube_url}">YouTube Music / Video</a>')
        else:
            query_enc = self.search_query.replace(' ', '+')
            links.append(f'• <a href="https://www.youtube.com/results?search_query={query_enc}">YouTube Search</a>')

        if self.spotify_url:
            links.append(f'• <a href="{self.spotify_url}">Spotify</a>')
        else:
            query_enc = self.search_query.replace(' ', '%20')
            links.append(f'• <a href="https://open.spotify.com/search/{query_enc}">Spotify Search</a>')

        if self.apple_music_url:
            links.append(f'• <a href="{self.apple_music_url}">Apple Music</a>')

        if self.shazam_url:
            links.append(f'• <a href="{self.shazam_url}">Shazam</a>')

        return "\n".join(links) if links else "• <i>No direct streaming links found</i>"

    def build_inline_keyboard(self) -> InlineKeyboardMarkup:
        """Build clickable inline buttons to listen on various platforms."""
        keyboard: List[List[InlineKeyboardButton]] = []
        row1: List[InlineKeyboardButton] = []

        # YouTube link
        yt = self.youtube_url or f"https://www.youtube.com/results?search_query={self.search_query.replace(' ', '+')}"
        row1.append(InlineKeyboardButton("🔴 YouTube", url=yt))

        # Spotify link
        sp = self.spotify_url or f"https://open.spotify.com/search/{self.search_query.replace(' ', '%20')}"
        row1.append(InlineKeyboardButton("🟢 Spotify", url=sp))
        keyboard.append(row1)

        row2: List[InlineKeyboardButton] = []
        if self.apple_music_url:
            row2.append(InlineKeyboardButton("🍎 Apple Music", url=self.apple_music_url))
        if self.shazam_url:
            row2.append(InlineKeyboardButton("🔵 Shazam", url=self.shazam_url))
        if row2:
            keyboard.append(row2)

        # Official Channel button
        keyboard.append([InlineKeyboardButton("📢 Channel @reki_anime_news", url="https://t.me/reki_anime_news")])
        return InlineKeyboardMarkup(keyboard)


class MusicRecognizer:
    def __init__(self):
        self.shazam = Shazam()

    async def extract_audio_snippet(
        self,
        input_path: str,
        output_path: str,
        duration: int = 12,
        start_offset: int = 0
    ) -> bool:
        """
        Extract a normalized 12-second audio snippet using ffmpeg.
        Converts any media (voice, video, audio) into 44.1kHz mono WAV for high-accuracy Shazam matching.
        """
        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-ss", str(start_offset),
                "-i", input_path,
                "-t", str(duration),
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                "-ac", "1",
                output_path
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await process.communicate()
            if process.returncode != 0:
                logger.warning(f"ffmpeg snippet extraction failed (rc={process.returncode}): {stderr.decode(errors='ignore')}")
                return False
            return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
        except Exception as e:
            logger.error(f"Error executing ffmpeg: {e}")
            return False

    async def recognize(self, media_path: str) -> Optional[TrackInfo]:
        """
        Analyze audio and identify the track using Shazam.
        Handles both raw files and auto-extracts snippets if needed.
        """
        snippet_path = f"{media_path}_snippet.wav"
        target_path = media_path

        try:
            extracted = await self.extract_audio_snippet(media_path, snippet_path)
            if extracted:
                target_path = snippet_path

            logger.info(f"Submitting audio fingerprint for: {target_path}")
            result = await self.shazam.recognize(target_path)

            if not result or not result.get('track'):
                logger.info("Shazam returned no matching track.")
                if extracted and os.path.getsize(media_path) > 300_000:
                    snippet_path_2 = f"{media_path}_snippet2.wav"
                    if await self.extract_audio_snippet(media_path, snippet_path_2, duration=12, start_offset=8):
                        result = await self.shazam.recognize(snippet_path_2)
                        try:
                            if os.path.exists(snippet_path_2):
                                os.remove(snippet_path_2)
                        except Exception:
                            pass

            if not result or not result.get('track'):
                return None

            return self._parse_track(result['track'])

        except Exception as e:
            logger.error(f"Error during music recognition: {e}", exc_info=True)
            return None
        finally:
            for p in (snippet_path, f"{media_path}_snippet2.wav"):
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

    def _parse_track(self, track: Dict[str, Any]) -> TrackInfo:
        """Parse raw Shazam track dictionary into a structured TrackInfo object."""
        track_id = str(track.get('key', ''))
        title = track.get('title', 'Unknown Title')
        artist = track.get('subtitle', 'Unknown Artist')

        # High resolution cover art
        images = track.get('images', {})
        cover_url = images.get('coverarthq') or images.get('coverart') or images.get('background')

        # Genres
        genres = track.get('genres', {})
        genre = genres.get('primary', 'Music')

        # Album & Release Year
        album = "Single"
        release_year = ""
        sections = track.get('sections', [])
        for section in sections:
            if section.get('type') == 'SONG':
                for meta in section.get('metadata', []):
                    title_lower = meta.get('title', '').lower()
                    if title_lower == 'album':
                        album = meta.get('text', album)
                    elif title_lower in ('released', 'year'):
                        release_year = meta.get('text', release_year)

        # Links
        shazam_url = track.get('url')
        apple_music_url = None
        youtube_url = None
        spotify_url = None

        hub = track.get('hub', {})
        for action in hub.get('actions', []):
            uri = action.get('uri', '')
            if 'music.apple.com' in uri:
                apple_music_url = uri

        for provider in hub.get('providers', []):
            for action in provider.get('actions', []):
                uri = action.get('uri', '')
                if 'spotify' in uri:
                    spotify_url = uri

        for section in sections:
            if section.get('type') == 'VIDEO':
                youtube_url = section.get('youtubeurl')

        return TrackInfo(
            track_id=track_id,
            title=title,
            artist=artist,
            album=album,
            genre=genre,
            release_year=release_year,
            cover_url=cover_url,
            shazam_url=shazam_url,
            apple_music_url=apple_music_url,
            youtube_url=youtube_url,
            spotify_url=spotify_url,
            raw_data=track
        )
