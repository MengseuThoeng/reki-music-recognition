# 🎵 Reki Music Recognition Bot

An asynchronous, high-performance Telegram bot that identifies any music playing around you or from media clips (Voice Notes, Audio files, Videos, Video Notes, and Social Links) and immediately delivers the track's cover art, metadata, and direct streaming links!

Built with 100% brand consistency under the **Reki Bot Ecosystem** by **[@RekiReze](https://t.me/RekiReze)**.

---

## ✨ Features

- 🎧 **Acoustic Fingerprinting**: Powered by `ShazamIO` with lightning-fast `ffmpeg` snippet extraction.
- 🖼 **High-Res Album Artwork**: Sends the official track cover poster with every recognized song.
- 📥 **All Media Formats Supported**:
  - 🎤 **Voice Notes**: Record ambient music in a cafe or car (3–10 seconds).
  - 🎵 **Audio Files**: Send any MP3, M4A, or WAV file.
  - 📹 **Videos & Video Notes**: Send video files or circular camera messages.
  - 🔗 **Links**: Paste TikTok or Instagram Reels links to extract and identify background audio.
- 🔗 **Direct Streaming Links & Quick Buttons**: Direct links and interactive inline buttons for YouTube Music, Spotify, Apple Music, and Shazam.
- ⚡ **Smart Song Cache**: Automatically caches recognized song metadata in SQLite for instant lookups.
- 🌐 **Full Dual-Language Support**: Complete Khmer (`km`) and English (`en`) localization with in-memory caching and persistent user preferences.
- 🛡 **High Concurrency & Stability**: Async pipeline with semaphore resource locking, SQLite WAL (Write-Ahead Logging) mode, and non-blocking `asyncio.to_thread` execution.

---

## 🛠 Tech Stack

- **Framework:** `python-telegram-bot==21.10` (Async application with `concurrent_updates=True`)
- **Recognition:** `shazamio` (Async acoustic fingerprinting engine)
- **Audio Extraction:** `ffmpeg` (+ `yt-dlp` for link audio extraction)
- **Database:** SQLite with WAL mode (`sqlite3` standard library - zero external database setup required)
- **Environment:** `python-dotenv`
- **Containerization:** Docker & Docker Compose

---

## 📂 Project Architecture

```text
reki-music-recogition/
├── bot.py                  # Main Telegram bot application & update handlers
├── database.py             # SQLite manager (WAL mode, async wrappers)
├── downloader.py           # Stream extractor for TikTok/Reels/Shorts links
├── recognizer.py           # ShazamIO acoustic recognition & ffmpeg slicing
├── locales.py              # Khmer & English translations & formatting
├── requirements.txt        # Python dependency manifest
├── Dockerfile              # Production Docker build with FFmpeg
├── docker-compose.yml      # Container orchestration
├── .env.example            # Environment variables template
└── README.md               # Documentation
```

---

## 🚀 Quick Setup & Deployment

### 1. Setup Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your bot token:
```env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
ADMIN_USER_IDS=123456789
SQLITE_DB_PATH=reki_music.db
```

### 2. Run with Docker Compose
```bash
docker compose up -d --build
```

### 3. Run Locally (Python 3.11+)
Make sure `ffmpeg` is installed on your machine.
```bash
pip install -r requirements.txt
python bot.py
```

---

## 📌 Bot Commands

| Command | Description |
| :--- | :--- |
| `/start` | Welcome menu, service introduction, and language selector |
| `/help` | 1-2-3 step-by-step user manual |
| `/about` | Bot version, architecture, and developer credits |
| `/language` | Switch between 🇰🇭 ភាសាខ្មែរ and 🇬🇧 English |
| `/stats` | *(Admin only)* Total users, requests, and cache metrics |
| `/mode` | *(Admin only)* Toggle maintenance or update modes |

---

## 👨‍💻 Developer & Brand

- **Developer:** [@RekiReze](https://t.me/RekiReze)
- **Official Channel:** [@reki_anime_news](https://t.me/reki_anime_news)
- **Ecosystem:** Reki Bot Ecosystem
