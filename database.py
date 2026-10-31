"""
Database manager for Reki Music Recognition Bot.
Uses Python's built-in SQLite with WAL mode and asyncio.to_thread wrappers.
Handles users, song metadata cache, and search logs.
Developer: @RekiReze
"""

import os
import sqlite3
import logging
import asyncio
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("SQLITE_DB_PATH", os.path.abspath("reki_music.db"))


def get_connection() -> sqlite3.Connection:
    """Create a connection to the SQLite database with WAL mode enabled."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db() -> bool:
    """Initialize database tables and indexes."""
    queries = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            language_code TEXT DEFAULT 'km',
            total_requests INTEGER DEFAULT 0,
            successful_searches INTEGER DEFAULT 0,
            failed_searches INTEGER DEFAULT 0,
            first_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS song_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shazam_id TEXT UNIQUE NOT NULL,
            title TEXT,
            artist TEXT,
            album TEXT,
            genre TEXT,
            cover_url TEXT,
            youtube_url TEXT,
            spotify_url TEXT,
            apple_music_url TEXT,
            shazam_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS search_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            input_type TEXT,
            status TEXT NOT NULL,
            shazam_id TEXT,
            query_title TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_song_cache_shazam ON song_cache(shazam_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_search_logs_user ON search_logs(user_id);
        """
    ]

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            for q in queries:
                cursor.execute(q)
            conn.commit()
        logger.info(f"✅ SQLite database initialized at: {DB_PATH}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize SQLite database: {e}", exc_info=True)
        return False


_mem_languages: Dict[int, str] = {}


# Async wrappers using asyncio.to_thread

async def async_init_db() -> bool:
    """Asynchronously initialize SQLite database schema."""
    return await asyncio.to_thread(init_db)


async def async_register_or_update_user(
    user_id: int,
    username: Optional[str],
    full_name: Optional[str],
    is_success: bool = True,
    language_code: Optional[str] = None
):
    """Register a new user or increment their search stats."""
    def _run():
        success_inc = 1 if is_success else 0
        failed_inc = 0 if is_success else 1
        lang = language_code or _mem_languages.get(user_id, 'km')

        try:
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO users (user_id, username, full_name, language_code, total_requests, successful_searches, failed_searches, last_used_at)
                    VALUES (?, ?, ?, ?, 1, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = excluded.username,
                        full_name = excluded.full_name,
                        language_code = COALESCE(excluded.language_code, users.language_code),
                        total_requests = users.total_requests + 1,
                        successful_searches = users.successful_searches + ?,
                        failed_searches = users.failed_searches + ?,
                        last_used_at = CURRENT_TIMESTAMP;
                """, (
                    user_id, username, full_name, lang,
                    success_inc, failed_inc,
                    success_inc, failed_inc
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error in async_register_or_update_user: {e}")

    await asyncio.to_thread(_run)


async def async_get_user_language(user_id: int, default: str = 'km') -> str:
    """Retrieve user language preference ('km' or 'en')."""
    if user_id in _mem_languages:
        return _mem_languages[user_id]

    def _run() -> str:
        try:
            with get_connection() as conn:
                row = conn.execute("SELECT language_code FROM users WHERE user_id = ?;", (user_id,)).fetchone()
                if row and row['language_code']:
                    _mem_languages[user_id] = row['language_code']
                    return row['language_code']
        except Exception as e:
            logger.warning(f"Error reading user language: {e}")
        return default

    return await asyncio.to_thread(_run)


async def async_set_user_language(user_id: int, language_code: str):
    """Update user language preference."""
    _mem_languages[user_id] = language_code

    def _run():
        try:
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO users (user_id, language_code, last_used_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id) DO UPDATE SET
                        language_code = excluded.language_code,
                        last_used_at = CURRENT_TIMESTAMP;
                """, (user_id, language_code))
                conn.commit()
        except Exception as e:
            logger.error(f"Error setting user language: {e}")

    await asyncio.to_thread(_run)


async def async_get_cached_song(shazam_id: str) -> Optional[Dict[str, Any]]:
    """Look up cached song metadata by Shazam track ID."""
    def _run() -> Optional[Dict[str, Any]]:
        if not shazam_id:
            return None
        try:
            with get_connection() as conn:
                row = conn.execute("""
                    SELECT shazam_id, title, artist, album, genre, cover_url, youtube_url, spotify_url, apple_music_url, shazam_url
                    FROM song_cache
                    WHERE shazam_id = ?;
                """, (str(shazam_id),)).fetchone()
                if row:
                    return dict(row)
        except Exception as e:
            logger.error(f"Error fetching cached song: {e}")
        return None

    return await asyncio.to_thread(_run)


async def async_add_to_song_cache(
    shazam_id: str,
    title: str = "",
    artist: str = "",
    album: str = "",
    genre: str = "",
    cover_url: Optional[str] = None,
    youtube_url: Optional[str] = None,
    spotify_url: Optional[str] = None,
    apple_music_url: Optional[str] = None,
    shazam_url: Optional[str] = None
):
    """Save recognized song metadata to cache."""
    def _run():
        if not shazam_id:
            return
        try:
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO song_cache (shazam_id, title, artist, album, genre, cover_url, youtube_url, spotify_url, apple_music_url, shazam_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (shazam_id) DO UPDATE SET
                        title = excluded.title,
                        artist = excluded.artist,
                        album = excluded.album,
                        genre = excluded.genre,
                        cover_url = excluded.cover_url,
                        youtube_url = excluded.youtube_url,
                        spotify_url = excluded.spotify_url,
                        apple_music_url = excluded.apple_music_url,
                        shazam_url = excluded.shazam_url;
                """, (str(shazam_id), title, artist, album, genre, cover_url, youtube_url, spotify_url, apple_music_url, shazam_url))
                conn.commit()
                logger.info(f"✅ Cached song metadata: {shazam_id} ({title})")
        except Exception as e:
            logger.error(f"Error caching song: {e}")

    await asyncio.to_thread(_run)


async def async_log_search(
    user_id: int,
    input_type: str,
    status: str,
    shazam_id: Optional[str] = None,
    query_title: Optional[str] = None,
    error_message: Optional[str] = None
):
    """Log search history for analytics and troubleshooting."""
    def _run():
        try:
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO search_logs (user_id, input_type, status, shazam_id, query_title, error_message)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (user_id, input_type, status, shazam_id, query_title, error_message))
                conn.commit()
        except Exception as e:
            logger.warning(f"Error logging search: {e}")

    await asyncio.to_thread(_run)


async def async_get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get system setting from database."""
    def _run() -> Optional[str]:
        try:
            with get_connection() as conn:
                row = conn.execute("SELECT value FROM bot_settings WHERE key = ?;", (key,)).fetchone()
                if row:
                    return row['value']
        except Exception as e:
            logger.warning(f"Error getting setting {key}: {e}")
        return default

    return await asyncio.to_thread(_run)


async def async_set_setting(key: str, value: str):
    """Update system setting."""
    def _run():
        try:
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO bot_settings (key, value)
                    VALUES (?, ?)
                    ON CONFLICT (key) DO UPDATE SET value = excluded.value;
                """, (key, value))
                conn.commit()
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")

    await asyncio.to_thread(_run)


async def async_get_admin_stats() -> Dict[str, Any]:
    """Retrieve statistical data for admin panel."""
    def _run() -> Dict[str, Any]:
        stats = {
            'total_users': 0,
            'total_requests': 0,
            'successful_searches': 0,
            'failed_searches': 0,
            'cached_songs': 0
        }
        try:
            with get_connection() as conn:
                row = conn.execute("""
                    SELECT 
                        COUNT(*) as total_users,
                        COALESCE(SUM(total_requests), 0) as total_requests,
                        COALESCE(SUM(successful_searches), 0) as successful_searches,
                        COALESCE(SUM(failed_searches), 0) as failed_searches
                    FROM users;
                """).fetchone()
                if row:
                    stats['total_users'] = row['total_users']
                    stats['total_requests'] = row['total_requests']
                    stats['successful_searches'] = row['successful_searches']
                    stats['failed_searches'] = row['failed_searches']

                cache_row = conn.execute("SELECT COUNT(*) as cached_songs FROM song_cache;").fetchone()
                if cache_row:
                    stats['cached_songs'] = cache_row['cached_songs']
        except Exception as e:
            logger.error(f"Error getting admin stats: {e}")
        return stats

    return await asyncio.to_thread(_run)
