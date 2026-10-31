Project Specification: Telegram Music Recognition & Audio Delivery Bot
1. Objective
Build a production-ready, asynchronous Python Telegram bot that identifies music (like Shazam) from user-submitted media (voice notes, audio files, video clips, or circular video notes) and replies with:
1. The recognized song's metadata (Cover Art, Title, Artist, Album, Release Year, and streaming links).
2. The full playable MP3 audio file downloaded automatically and sent directly into the chat.
2. Tech Stack & Dependencies
- Language: Python 3.11+
- Bot Framework: aiogram (v3.x) for asynchronous Telegram API handling.
- Music Recognition: shazamio for acoustic fingerprinting and track metadata lookup.
- Audio Fetching: yt-dlp for searching and extracting the full audio stream in .mp3 format.
- System Dependencies: ffmpeg (required by both shazamio and yt-dlp for audio conversion and metadata embedding).
- Caching / Database: aiosqlite (or local JSON/SQLite) to cache shazam_track_id -> telegram_file_id so previously requested songs are sent instantaneously without re-downloading.
- Deployment: Dockerfile and docker-compose.yml for one-command deployment.
3. Project Directory Structure
Create the following clean modular structure:
music-recognition-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Entry point, bot & dispatcher initialization
│   ├── config.py            # Environment variables loader (pydantic-settings or python-dotenv)
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py         # /start and /help command handlers
│   │   └── media.py         # Voice, audio, video, and video_note handlers
│   ├── services/
│   │   ├── __init__.py
│   │   ├── recognizer.py    # ShazamIO integration logic
│   │   ├── downloader.py    # yt-dlp search & MP3 extraction logic
│   │   └── cache.py         # SQLite caching for Telegram file_ids
│   └── utils/
│       ├── __init__.py
│       └── cleanup.py       # Context manager or helper to safely delete temp files
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md