"""
Music recognition service for Reki Music Recognition Bot.
Uses ShazamIO for acoustic fingerprinting and ffmpeg for audio snippet extraction.
Developer: @RekiReze
"""

import os
import logging
import asyncio
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from shazamio import Shazam

logger = logging.getLogger(__name__)


def sanitize_https_url(url: Optional[str]) -> Optional[str]:
    """Ensure URL starts with http:// or https://, otherwise return None."""
    if not url:
        return None
    url = str(url).strip()
    if url.startswith("https://") or url.startswith("http://"):
        return url
    if url.startswith("//"):
        return "https:" + url
    return None


def format_spotify_url(uri: Optional[str], query: str) -> str:
    """Convert Spotify URI or raw string into a valid https://open.spotify.com URL."""
    if uri:
        uri = str(uri).strip()
        if uri.startswith("https://open.spotify.com/"):
            return uri
        if uri.startswith("spotify:track:"):
            track_id = uri.split(":")[-1]
            return f"https://open.spotify.com/track/{track_id}"
        if uri.startswith("spotify:search:"):
            search_param = uri.split(":", 2)[-1]
            return f"https://open.spotify.com/search/{search_param}"
    encoded = urllib.parse.quote(query)
    return f"https://open.spotify.com/search/{encoded}"


def format_apple_music_url(uri: Optional[str]) -> Optional[str]:
    """Convert Apple Music URI into a valid https:// URL."""
    if not uri:
        return None
    uri = str(uri).strip()
    if uri.startswith("https://") or uri.startswith("http://"):
        return uri
    if uri.startswith("itmss://"):
        return "https://" + uri[8:]
    return None


def format_youtube_url(url: Optional[str], query: str) -> str:
    """Ensure YouTube URL is a valid https:// URL."""
    valid_url = sanitize_https_url(url)
    if valid_url:
        return valid_url
    encoded = urllib.parse.quote_plus(query)
    return f"https://www.youtube.com/results?search_query={encoded}"


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

    def get_clean_youtube_url(self) -> str:
        return format_youtube_url(self.youtube_url, self.search_query)

    def get_clean_spotify_url(self) -> str:
        return format_spotify_url(self.spotify_url, self.search_query)

    def get_clean_apple_music_url(self) -> Optional[str]:
        return format_apple_music_url(self.apple_music_url)

    def get_clean_shazam_url(self) -> Optional[str]:
        return sanitize_https_url(self.shazam_url)

    def format_links_html(self) -> str:
        """Format streaming service links into clean HTML bullet points."""
        links: List[str] = []
        yt = self.get_clean_youtube_url()
        sp = self.get_clean_spotify_url()
        am = self.get_clean_apple_music_url()
        sh = self.get_clean_shazam_url()

        links.append(f'• <a href="{yt}">YouTube Music / Video</a>')
        links.append(f'• <a href="{sp}">Spotify</a>')
        if am:
            links.append(f'• <a href="{am}">Apple Music</a>')
        if sh:
            links.append(f'• <a href="{sh}">Shazam</a>')

        return "\n".join(links)

    def build_inline_keyboard(self) -> InlineKeyboardMarkup:
        """Build clickable inline buttons with guaranteed valid HTTPS URLs."""
        keyboard: List[List[InlineKeyboardButton]] = []
        row1: List[InlineKeyboardButton] = []

        yt = self.get_clean_youtube_url()
        sp = self.get_clean_spotify_url()
        am = self.get_clean_apple_music_url()
        sh = self.get_clean_shazam_url()

        if yt and yt.startswith("http"):
            row1.append(InlineKeyboardButton("🔴 YouTube", url=yt))
        if sp and sp.startswith("http"):
            row1.append(InlineKeyboardButton("🟢 Spotify", url=sp))
        if row1:
            keyboard.append(row1)

        row2: List[InlineKeyboardButton] = []
        if am and am.startswith("http"):
            row2.append(InlineKeyboardButton("🍎 Apple Music", url=am))
        if sh and sh.startswith("http"):
            row2.append(InlineKeyboardButton("🔵 Shazam", url=sh))
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
        cover_url = sanitize_https_url(cover_url)

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
        shazam_url = sanitize_https_url(track.get('url'))
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
