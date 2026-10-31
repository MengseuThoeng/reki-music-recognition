"""
Reki Music Recognition Bot
Part of the Reki Bot Ecosystem.
Developer: @RekiReze
Official Channel: @reki_anime_news

Framework: python-telegram-bot==21.10
Recognition Engine: ShazamIO + FFmpeg
Database: SQLite with WAL mode & async wrappers
"""

import os
import re
import uuid
import logging
import asyncio
from typing import Dict, Optional, Set
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from dotenv import load_dotenv

from locales import t
from recognizer import MusicRecognizer, TrackInfo
from downloader import MediaExtractor
from database import (
    async_init_db,
    async_register_or_update_user,
    async_get_cached_song,
    async_add_to_song_cache,
    async_log_search,
    async_get_user_language,
    async_set_user_language,
    async_get_setting,
    async_set_setting,
    async_get_admin_stats
)

# Load environment
load_dotenv()

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Configuration & Flags
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_USER_IDS = [int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip().isdigit()]
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "20"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
UPDATE_MODE = os.getenv("UPDATE_MODE", "false").lower() == "true"

# Service instances
recognizer = MusicRecognizer()
extractor = MediaExtractor()

# Concurrency & Task trackers
task_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
active_tasks: Set[asyncio.Task] = set()

# In-memory language cache for instant lookups
user_languages: Dict[int, str] = {}


def is_admin(user_id: int) -> bool:
    """Check if given Telegram user is an admin."""
    return user_id in ADMIN_USER_IDS


def escape_html(text: Optional[str]) -> str:
    """Escape HTML sensitive characters."""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


async def get_user_lang(user_id: int, telegram_lang_code: Optional[str] = None) -> str:
    """Resolve preferred language ('km' or 'en')."""
    if user_id in user_languages:
        return user_languages[user_id]

    db_lang = await async_get_user_language(user_id, default=None)
    if db_lang:
        user_languages[user_id] = db_lang
        return db_lang

    lang = 'en' if telegram_lang_code and telegram_lang_code.lower().startswith('en') else 'km'
    user_languages[user_id] = lang
    return lang


def extract_first_url(text: str) -> Optional[str]:
    """Extract first HTTP/HTTPS URL from text."""
    match = re.search(r'(https?://[^\s]+)', text)
    return match.group(0) if match else None


# ==============================================================================
# Command Handlers
# ==============================================================================

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    if not user:
        return

    lang = await get_user_lang(user.id, user.language_code)
    await async_register_or_update_user(user.id, user.username, user.full_name, is_success=True, language_code=lang)

    # Check maintenance & update modes
    if MAINTENANCE_MODE and not is_admin(user.id):
        await update.message.reply_html(t('maintenance_active', lang))
        return

    if UPDATE_MODE and not is_admin(user.id):
        await update.message.reply_html(t('update_active', lang))
        return

    name = escape_html(user.first_name or "Friend")
    welcome_text = t('welcome', lang, name=name)

    keyboard = [
        [
            InlineKeyboardButton("🇰🇭 ភាសាខ្មែរ", callback_data="lang_km"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        ],
        [
            InlineKeyboardButton("📢 Official Channel", url="https://t.me/reki_anime_news"),
            InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/RekiReze")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_html(
        welcome_text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    user = update.effective_user
    lang = await get_user_lang(user.id, user.language_code) if user else 'km'
    await update.message.reply_html(t('help', lang), disable_web_page_preview=True)


async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command."""
    user = update.effective_user
    lang = await get_user_lang(user.id, user.language_code) if user else 'km'

    keyboard = [
        [
            InlineKeyboardButton("📢 Channel", url="https://t.me/reki_anime_news"),
            InlineKeyboardButton("💬 Support", url="https://t.me/RekiReze")
        ]
    ]
    await update.message.reply_html(
        t('about', lang),
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )


async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /language command."""
    user = update.effective_user
    lang = await get_user_lang(user.id, user.language_code) if user else 'km'

    keyboard = [
        [
            InlineKeyboardButton("🇰🇭 ភាសាខ្មែរ", callback_data="lang_km"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        ]
    ]
    await update.message.reply_html(
        t('lang_select', lang),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def language_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection button callbacks."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    if not user:
        return

    data = query.data
    selected_lang = 'en' if data == 'lang_en' else 'km'

    user_languages[user.id] = selected_lang
    await async_set_user_language(user.id, selected_lang)

    confirm_text = t('lang_changed', selected_lang)
    await query.edit_message_text(confirm_text, parse_mode="HTML")


# ==============================================================================
# Admin Handlers
# ==============================================================================

async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats for administrators."""
    user = update.effective_user
    if not user or not is_admin(user.id):
        return

    stats = await async_get_admin_stats()
    text = (
        "📊 <b>ស្ថិតិប្រព័ន្ធ (Reki Music Bot Stats)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: <code>{stats['total_users']:,}</code>\n"
        f"🔍 Total Requests: <code>{stats['total_requests']:,}</code>\n"
        f"✅ Successful Searches: <code>{stats['successful_searches']:,}</code>\n"
        f"❌ Failed Searches: <code>{stats['failed_searches']:,}</code>\n"
        f"⚡ Cached Tracks: <code>{stats['cached_songs']:,}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠 Maintenance: <code>{MAINTENANCE_MODE}</code>\n"
        f"🚀 Update Mode: <code>{UPDATE_MODE}</code>"
    )
    await update.message.reply_html(text)


async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle maintenance or update mode: /mode maintenance on/off."""
    global MAINTENANCE_MODE, UPDATE_MODE
    user = update.effective_user
    if not user or not is_admin(user.id):
        return

    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text("Usage: /mode [maintenance|update] [on|off]")
        return

    target = args[0].lower()
    state = args[1].lower() == "on"

    if target == "maintenance":
        MAINTENANCE_MODE = state
        await async_set_setting("maintenance_mode", str(state).lower())
        await update.message.reply_text(f"Maintenance mode set to: {state}")
    elif target == "update":
        UPDATE_MODE = state
        await async_set_setting("update_mode", str(state).lower())
        await update.message.reply_text(f"Update mode set to: {state}")
    else:
        await update.message.reply_text("Invalid target. Use 'maintenance' or 'update'")


# ==============================================================================
# Core Music Recognition Workflow
# ==============================================================================

async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Spawn background task for voice, audio, video, video_note, and URLs."""
    user = update.effective_user
    message = update.message
    if not user or not message:
        return

    lang = await get_user_lang(user.id, user.language_code)
    if MAINTENANCE_MODE and not is_admin(user.id):
        await message.reply_html(t('maintenance_active', lang))
        return
    if UPDATE_MODE and not is_admin(user.id):
        await message.reply_html(t('update_active', lang))
        return

    task = asyncio.create_task(process_music_request(update, context, lang))
    active_tasks.add(task)
    task.add_done_callback(active_tasks.discard)


async def process_music_request(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    """Core pipeline: Download input snippet -> Fingerprint -> Deliver Song Info & Cover Art."""
    user = update.effective_user
    message = update.message
    if not user or not message:
        return

    async with task_semaphore:
        status_msg = None
        temp_input_path = None
        input_type = "unknown"

        try:
            status_msg = await message.reply_html(t('listening', lang))

            # 1. Determine input media
            file_id = None
            file_size = 0
            url = None

            if message.voice:
                input_type = "voice"
                file_id = message.voice.file_id
                file_size = message.voice.file_size or 0
                ext = ".ogg"
            elif message.audio:
                input_type = "audio"
                file_id = message.audio.file_id
                file_size = message.audio.file_size or 0
                ext = ".mp3"
            elif message.video:
                input_type = "video"
                file_id = message.video.file_id
                file_size = message.video.file_size or 0
                ext = ".mp4"
            elif message.video_note:
                input_type = "video_note"
                file_id = message.video_note.file_id
                file_size = message.video_note.file_size or 0
                ext = ".mp4"
            elif message.document:
                mime = message.document.mime_type or ""
                if mime.startswith("audio") or mime.startswith("video"):
                    input_type = "document"
                    file_id = message.document.file_id
                    file_size = message.document.file_size or 0
                    ext = ".mp4" if mime.startswith("video") else ".mp3"
                else:
                    await status_msg.edit_text(t('invalid_input', lang), parse_mode="HTML")
                    return
            elif message.text:
                url = extract_first_url(message.text)
                if not url:
                    await status_msg.edit_text(t('invalid_input', lang), parse_mode="HTML")
                    return
                input_type = "url"
            else:
                await status_msg.edit_text(t('invalid_input', lang), parse_mode="HTML")
                return

            # Check file size limit
            if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                await status_msg.edit_text(t('file_too_large', lang, max_size=MAX_FILE_SIZE_MB), parse_mode="HTML")
                return

            # 2. Acquire media on disk
            uid = uuid.uuid4().hex[:8]
            if url:
                temp_input_path = await extractor.extract_audio_from_link(url)
                if not temp_input_path:
                    await status_msg.edit_text(t('song_not_found', lang), parse_mode="HTML")
                    await async_log_search(user.id, input_type, status="failed", error_message="URL audio extraction failed")
                    return
            else:
                temp_input_path = os.path.abspath(os.path.join(extractor.download_dir, f"input_{uid}{ext}"))
                tg_file = await context.bot.get_file(file_id)
                await tg_file.download_to_drive(custom_path=temp_input_path)

            # 3. Acoustic fingerprinting via ShazamIO
            track: Optional[TrackInfo] = await recognizer.recognize(temp_input_path)

            if not track:
                await status_msg.edit_text(t('song_not_found', lang), parse_mode="HTML")
                await async_register_or_update_user(user.id, user.username, user.full_name, is_success=False)
                await async_log_search(user.id, input_type, status="not_found")
                return

            # 4. Format song metadata
            delivery_text = t(
                'song_found',
                lang,
                title=escape_html(track.title),
                artist=escape_html(track.artist),
                album=escape_html(track.album),
                genre=escape_html(track.genre),
                links=track.format_links_html()
            )

            keyboard = track.build_inline_keyboard()

            # 5. Deliver Song Information & Cover Art
            if track.cover_url:
                try:
                    await message.reply_photo(
                        photo=track.cover_url,
                        caption=delivery_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                except Exception as e:
                    logger.warning(f"Failed to send cover photo ({e}), falling back to text reply.")
                    await message.reply_html(
                        delivery_text,
                        reply_markup=keyboard,
                        disable_web_page_preview=False
                    )
            else:
                await message.reply_html(
                    delivery_text,
                    reply_markup=keyboard,
                    disable_web_page_preview=False
                )

            # Delete the temporary status message
            try:
                await status_msg.delete()
            except Exception:
                pass

            # 6. Save in SQLite cache & update user stats
            await async_add_to_song_cache(
                shazam_id=track.track_id,
                title=track.title,
                artist=track.artist,
                album=track.album,
                genre=track.genre,
                cover_url=track.cover_url,
                youtube_url=track.youtube_url,
                spotify_url=track.spotify_url,
                apple_music_url=track.apple_music_url,
                shazam_url=track.shazam_url
            )

            await async_register_or_update_user(user.id, user.username, user.full_name, is_success=True)
            await async_log_search(user.id, input_type, status="success", shazam_id=track.track_id, query_title=track.title)

        except Exception as e:
            logger.error(f"Error processing music request: {e}", exc_info=True)
            if status_msg:
                try:
                    await status_msg.edit_text(t('error_general', lang), parse_mode="HTML")
                except Exception:
                    pass
            await async_log_search(user.id, input_type, status="error", error_message=str(e))

        finally:
            MediaExtractor.cleanup_file(temp_input_path)


# ==============================================================================
# Bot Setup & Initialization
# ==============================================================================

async def post_init(application: Application):
    """Set bot commands and initialize database on startup."""
    logger.info("Initializing SQLite database...")
    await async_init_db()

    commands = [
        BotCommand("start", "Start the bot & show welcome menu"),
        BotCommand("help", "How to recognize songs and use the bot"),
        BotCommand("about", "Bot info & developer credit"),
        BotCommand("language", "Change language / ផ្លាស់ប្តូរភាសា"),
    ]
    try:
        await application.bot.set_my_commands(commands)
        logger.info("✅ Bot commands registered successfully")
    except Exception as e:
        logger.warning(f"Failed to set bot commands: {e}")


def main():
    """Start the bot application."""
    if not TOKEN:
        logger.critical("TELEGRAM_BOT_TOKEN environment variable is missing!")
        print("Error: Please set TELEGRAM_BOT_TOKEN in your .env file.")
        return

    logger.info("Starting Reki Music Recognition Bot...")

    application = (
        Application.builder()
        .token(TOKEN)
        .concurrent_updates(True)
        .read_timeout(600)
        .write_timeout(600)
        .connect_timeout(180)
        .pool_timeout(180)
        .post_init(post_init)
        .build()
    )

    # Command handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("about", about_handler))
    application.add_handler(CommandHandler("language", language_handler))
    application.add_handler(CommandHandler("stats", stats_handler))
    application.add_handler(CommandHandler("mode", mode_handler))

    # Language selection callback
    application.add_handler(CallbackQueryHandler(language_callback_handler, pattern=r"^lang_"))

    # Media message handlers: Voice, Audio, Video, Video Note, Audio/Video Documents, URL links
    media_filters = (
        filters.VOICE |
        filters.AUDIO |
        filters.VIDEO |
        filters.VIDEO_NOTE |
        filters.Document.ALL |
        (filters.TEXT & filters.Entity("url"))
    )
    application.add_handler(MessageHandler(media_filters, media_handler))

    logger.info("🚀 Reki Music Recognition Bot is running (polling mode)...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
