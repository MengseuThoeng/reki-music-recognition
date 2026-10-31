# Reki Bot Ecosystem: Design System & Developer Blueprint

> **Purpose for AI / Developer:**
> This document specifies the exact personality, architecture, UI/UX language, code style, and developer signature for building the new **Reki Music Recognition Bot**. Any AI assistant or developer reading this must ensure that this bot **feels 100% like it was made by the exact same creator (`@RekiReze`) as the Reki Downloader Bot (`future-plan` branch)**.

---

## 1. Identity, Brand & Developer Signature

Every bot under the **Reki Bot Ecosystem** shares a single unified brand identity:

- **Developer:** `@RekiReze` (Always credit this handle in `/about`, error messages, and contact footers).
- **Official Channel:** `@reki_anime_news` (Always plugged in `/start`, `/about`, and media delivery captions).
- **Tone of Voice:**
  - **Khmer:** Polite, helpful, polished, modern Khmer tech tone (not archaic, not robotic). Uses clean bulleting, emojis, and clear verbs (`សូមស្វាគមន៍`, `សូមរង់ចាំបន្តិច`, `សូមព្យាយាមម្ដងទៀត`).
  - **English:** Crisp, friendly, concise developer English.
- **Format Consistency:**
  - Standard delimiter line: `━━━━━━━━━━━━━━━━━━━━` (used across all menu outputs and headers).
  - Code wrapping: Technical parameters, song titles, artist names, and command syntaxes must be wrapped in `<code>...</code>`.
  - Parse Mode: **Always HTML** (`parse_mode="HTML"`).

---

## 2. Localization System (`locales.py`)

All user-facing copy must reside in a separate `locales.py` module. **Never hardcode user-facing strings inside `bot.py`**.

### Structure:
```python
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'km': { ... }, # Khmer (Default)
    'en': { ... }, # English
}

def t(key: str, lang: str = 'km', **kwargs) -> str:
    """Helper function to fetch localized string with variable substitution."""
```

### Mandatory Command Dictionary Keys:
1. `'welcome'`: Sent upon `/start`.
2. `'help'`: Sent upon `/help`.
3. `'about'`: Sent upon `/about`.
4. `'lang_select'`: Prompt for language selection.
5. `'lang_changed'`: Confirmation when user picks a language.
6. `'listening'` / `'processing'`: Loading status indicator.
7. `'song_found'`: Structured template for successful recognition.
8. `'song_not_found'`: Friendly error when audio matches nothing.
9. `'invalid_input'`: When user sends unsupported media.
10. `'file_too_large'`: Standard 50MB Telegram Bot API warning.
11. `'error_general'`: Catch-all fallback error.
12. `'maintenance_active'`: Maintenance mode notice.
13. `'update_active'`: Update/Admin testing notice.
14. `'admin_only'`: Permission denied notice.

---

## 3. UI/UX & Command Layout Patterns

The command set must mirror the Downloader Bot standard:

| Command | Purpose | Behavior |
| :--- | :--- | :--- |
| `/start` | Welcome message | Introduces the bot, inputs supported, key commands, and sets command menu. |
| `/help` | User manual | 1-2-3 step guide with clear numbered icons (`1️⃣`, `2️⃣`, `3️⃣`). |
| `/about` | Bot & Dev metadata | Mentions version, features, stack, `@RekiReze`, and `@reki_anime_news`. |
| `/language` | Language switcher | Sends Inline Keyboard with `🇰🇭 ភាសាខ្មែរ` and `🇬🇧 English`. |

### Standard Message Templates

#### A. `/start` (Welcome) Pattern:
```html
👋 <b>សួស្ដី {name}! សូមស្វាគមន៍មកកាន់ Reki Music Finder Bot!</b>
━━━━━━━━━━━━━━━━━━━━
[1-sentence high-impact value proposition: recognize any audio/video song instantly]

📥 <b>សេវាកម្មដែលគាំទ្រ (Supported Inputs):</b>
  🎤 <b>Voice Note</b>: ថតសំឡេងភ្លេងដែលអ្នកកំពុងឮ (3-10 វិនាទី)
  🎵 <b>Audio File</b>: ផ្ញើ file ចម្រៀង ឬកាត់សំឡេង MP3/M4A/WAV
  📹 <b>Video</b>: ផ្ញើវីដេអូដែលមានចាក់បទភ្លេងនោះ
  🔗 <b>TikTok & Reels</b>: ផ្ញើ link វីដេអូដើម្បីឱ្យ bot ស្ដាប់

👉 <b>របៀបប្រើងាយៗ:</b> គ្រាន់តែ <b>ផ្ញើ Voice / Audio / Video / Link</b> មកកាន់ Bot នេះភ្លាម!
━━━━━━━━━━━━━━━━━━━━
📌 <b>ពាក្យបញ្ជា (Commands):</b>
• /start - បង្ហាញសារស្វាគមន៍នេះឡើងវិញ
• /help - ការណែនាំលម្អិតពីរបៀបប្រើ
• /about - អំពី Bot និង Developer
• /language - ផ្លាស់ប្តូរភាសា (Change Language)
```


#### B. `/help` (Step-by-Step Guide) Pattern:
```html
📖 <b>ការណែនាំពីរបៀបប្រើប្រាស់ (How to use):</b>
━━━━━━━━━━━━━━━━━━━━
1️⃣ <b>ឮបទចម្រៀងពីរោះ?</b> ឮភ្លេងនៅហាងកាហ្វេ វិទ្យុ ឬក្នុងទូរស័ព្ទ
2️⃣ <b>ផ្ញើចូល Bot:</b>
   • ចុច Record <b>Voice Note</b> ផ្ញើមក (យ៉ាងតិច 3-5 វិនាទី)
   • ឬ <b>Forward សារសំឡេង / វីដេអូ</b> ពី Chat ផ្សេងចូលមក
   • ឬ <b>Copy Link</b> វីដេអូ TikTok / IG ផ្ញើមក
3️⃣ <b>ទទួលយកលទ្ធផល:</b> Bot នឹងវិភាគរលកសំឡេង រួចបង្ហាញចំណងជើងបទ, អ្នកច្រៀង និង Link ស្ដាប់នៅលើ Spotify / YouTube ភ្លាមៗ! 🚀

⚠️ <b>ចំណាំសំខាន់:</b>
• បើកសំឡេងឱ្យឮច្បាស់ល្អ និងជៀសវាងសំឡេងរំខានខ្លាំងពេក
• កំណាត់សំឡេងខ្លីបំផុតគឺ 3 វិនាទី
```

#### C. `/about` (Official Brand) Pattern:
```html
ℹ️ <b>អំពីយើងខ្ញុំ / About Us</b>
━━━━━━━━━━━━━━━━━━━━
🤖 <b>Bot Name:</b> Reki Music Recognition Bot
⚡ <b>Version:</b> 1.0 (Acoustic Fingerprint Engine)
✨ <b>មុខងារចម្បង:</b>
  • ស្គាល់បទភ្លេងបានលឿន និងសុក្រឹត (Shazam Engine)
  • ផ្តល់តំណភ្ជាប់ (Links) ទៅកាន់ YouTube, Spotify, Apple Music
  • គាំទ្រការទាញយកសំឡេងពី TikTok & Instagram
  • គាំទ្រទាំងភាសាខ្មែរ និងអង់គ្លេស

👨‍💻 <b>Developer & Contact:</b>
  • <b>Developer:</b> @RekiReze
  • <b>Official Channel:</b> @reki_anime_news
  • <b>Platform:</b> Python, Telegram Bot API, PostgreSQL

❤️ សូមអរគុណដល់អ្នកទាំងអស់គ្នាដែលបានប្រើប្រាស់ និងគាំទ្រ Bot របស់យើងខ្ញុំ!
```

#### D. Song Recognized Delivery Pattern:
```html
🎶 <b>រកឃើញបទចម្រៀងហើយ!</b> 🎉
━━━━━━━━━━━━━━━━━━━━
🎵 <b>ចំណងជើង:</b> <code>{title}</code>
🎤 <b>អ្នកច្រៀង:</b> <code>{artist}</code>
💿 <b>អាល់ប៊ុម:</b> <code>{album}</code>
🏷️ <b>ប្រភេទ:</b> <code>{genre}</code>
━━━━━━━━━━━━━━━━━━━━
🔗 <b>តំណភ្ជាប់ស្ដាប់កម្សាន្ត:</b>
{links}

📢 សូមគាំទ្រដោយចូល Join Channel @reki_anime_news
```

---

## 4. Technical Architecture & Engineering Standards

### 1. Framework & Libraries
- **Telegram Wrapper:** `python-telegram-bot==21.10`
- **Application Builder:** Async application with `concurrent_updates(True)`.
- **Music Recognition Engine:** `shazamio` (Python async Shazam API wrapper).
- **Audio Processing:** `ffmpeg` (for slicing 5-10 second snippets, extracting audio streams from videos/voice notes).
- **Environment Management:** `python-dotenv`.
- **Database:** PostgreSQL (`psycopg2-binary`) using connection pooling with non-blocking async wrappers (`asyncio.to_thread`).

### 2. State & Database Conventions
Follow the database table pattern from `database.py`:
- `users`: Tracks `user_id`, `username`, `full_name`, `language_code` (`km`/`en`), `total_requests`, `successful_searches`, `first_used_at`, `last_used_at`.
- `song_cache`: Caches audio fingerprints / track hashes so repeated queries return immediately without contacting third-party APIs.
- `search_logs`: Logs every search attempt, latency, status (`success`/`failed`), and error message.

### 3. Concurrency & Safety Controls
- **Global Semaphore:** `asyncio.Semaphore(MAX_CONCURRENT_TASKS)` (default: 10) to guard CPU and network during audio processing.
- **Task Tracking:** Maintain `active_tasks = set()` to avoid garbage collection of running asyncio tasks.
- **Timeouts:**
  ```python
  Application.builder()
      .token(token)
      .concurrent_updates(True)
      .read_timeout(600)
      .write_timeout(600)
      .connect_timeout(180)
      .pool_timeout(180)
      .build()
  ```
- **Administrative Modes:**
  - `MAINTENANCE_MODE=true`: Temporarily blocks all queries with `maintenance_active` text.
  - `UPDATE_MODE=true`: Admin-only testing mode (`is_admin(user_id)` check against `ADMIN_USER_IDS`).

---

## 5. Summary Checklist for Any AI Building This Bot

Before considering the Reki Music Bot complete, verify:
- [ ] Is all text routed through `locales.py` with both `km` and `en` translations?
- [ ] Does `/start`, `/help`, and `/about` match the exact wording, divider line (`━━━━━━━━━━━━━━━━━━━━`), and emoji palette?
- [ ] Is `@RekiReze` cited as the developer in `/about` and all error notices?
- [ ] Is `@reki_anime_news` linked in delivery footers and welcome messages?
- [ ] Does it handle Voice Notes (`filters.VOICE`), Audio files (`filters.AUDIO`), and Videos (`filters.VIDEO`) seamlessly?
- [ ] Is `parse_mode="HTML"` used consistently with proper `escape_html()` sanitation?

