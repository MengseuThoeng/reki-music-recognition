"""
Localization / Multi-language support for Reki Music Recognition Bot.
Supported Languages:
  - km: Khmer (Default)
  - en: English
Developer: @RekiReze
Official Channel: @reki_anime_news
"""

from typing import Dict, Any


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'km': {
        # Commands & Help
        'welcome': (
            "👋 <b>សួស្ដី {name}! សូមស្វាគមន៍មកកាន់ Reki Music Finder Bot!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Bot នេះជួយអ្នកស្គាល់បទភ្លេង និងបង្ហាញព័ត៌មានលម្អិតពីបទចម្រៀងបានយ៉ាងរហ័ស និងសុក្រឹតបំផុត! 🎧⚡\n\n"
            "📥 <b>សេវាកម្មដែលគាំទ្រ (Supported Inputs):</b>\n"
            "  🎤 <b>Voice Note</b>: ថតសំឡេងភ្លេងដែលអ្នកកំពុងឮ (3-10 វិនាទី)\n"
            "  🎵 <b>Audio File</b>: ផ្ញើ file ចម្រៀង ឬកាត់សំឡេង MP3/M4A/WAV\n"
            "  📹 <b>Video</b>: ផ្ញើវីដេអូ ឬ Video Note (កាមេរ៉ាមូល) ដែលមានចាក់បទភ្លេងនោះ\n"
            "  🔗 <b>TikTok & Reels</b>: ផ្ញើ link វីដេអូដើម្បីឱ្យ bot ស្ដាប់ និងប្រាប់បទភ្លេង\n\n"
            "👉 <b>របៀបប្រើងាយៗ:</b> គ្រាន់តែ <b>ផ្ញើ Voice / Audio / Video / Link</b> មកកាន់ Bot នេះភ្លាម!\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📌 <b>ពាក្យបញ្ជា (Commands):</b>\n"
            "• /start - បង្ហាញសារស្វាគមន៍នេះឡើងវិញ\n"
            "• /help - ការណែនាំលម្អិតពីរបៀបប្រើ\n"
            "• /about - អំពី Bot និង Developer\n"
            "• /language - ផ្លាស់ប្តូរភាសា (Change Language)"
        ),
        'help': (
            "📖 <b>ការណែនាំពីរបៀបប្រើប្រាស់ (How to use):</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "1️⃣ <b>ឮបទចម្រៀងពីរោះ?</b> ឮភ្លេងនៅហាងកាហ្វេ វិទ្យុ ឬក្នុងទូរស័ព្ទ\n"
            "2️⃣ <b>ផ្ញើចូល Bot:</b>\n"
            "   • ចុច Record <b>Voice Note</b> ផ្ញើមក (យ៉ាងតិច 3-5 វិនាទី)\n"
            "   • ឬ <b>Forward សារសំឡេង / វីដេអូ</b> ពី Chat ផ្សេងចូលមក\n"
            "   • ឬ <b>Copy Link</b> វីដេអូ TikTok / IG ផ្ញើមក\n"
            "3️⃣ <b>ទទួលយកលទ្ធផល:</b> Bot នឹងវិភាគរលកសំឡេង រួចបង្ហាញរូបភាព Poster, ចំណងជើងបទ, អ្នកច្រៀង, អាល់ប៊ុម និង Link ស្ដាប់នៅលើ Spotify / YouTube / Apple Music ភ្លាមៗ! 🚀\n\n"
            "⚠️ <b>ចំណាំសំខាន់:</b>\n"
            "• បើកសំឡេងឱ្យឮច្បាស់ល្អ និងជៀសវាងសំឡេងរំខានខ្លាំងពេក\n"
            "• កំណាត់សំឡេងខ្លីបំផុតគឺ 3 វិនាទី"
        ),
        'about': (
            "ℹ️ <b>អំពីយើងខ្ញុំ / About Us</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 <b>Bot Name:</b> Reki Music Recognition Bot\n"
            "⚡ <b>Version:</b> 1.0 (Acoustic Fingerprint Engine)\n"
            "✨ <b>មុខងារចម្បង:</b>\n"
            "  • ស្គាល់បទភ្លេងបានលឿន និងសុក្រឹត (Shazam Engine)\n"
            "  • បង្ហាញរូបភាពគម្រប (Cover Art) និងព័ត៌មានបទចម្រៀង\n"
            "  • ផ្តល់តំណភ្ជាប់ (Links) ទៅកាន់ YouTube, Spotify, Apple Music\n"
            "  • គាំទ្រការទាញយកសំឡេងពី TikTok & Instagram\n"
            "  • គាំទ្រទាំងភាសាខ្មែរ និងអង់គ្លេស\n\n"
            "👨‍💻 <b>Developer & Contact:</b>\n"
            "  • <b>Developer:</b> @RekiReze\n"
            "  • <b>Official Channel:</b> @reki_anime_news\n"
            "  • <b>Platform:</b> Python, Telegram Bot API, SQLite\n\n"
            "❤️ សូមអរគុណដល់អ្នកទាំងអស់គ្នាដែលបានប្រើប្រាស់ និងគាំទ្រ Bot របស់យើងខ្ញុំ!"
        ),
        'lang_select': (
            "🌐 <b>សូមជ្រើសរើសភាសារបស់អ្នក / Please select your language:</b>"
        ),
        'lang_changed': (
            "✅ ភាសាត្រូវបានប្តូរទៅជា <b>🇰🇭 ភាសាខ្មែរ</b> ដោយជោគជ័យ!"
        ),

        # Status & Progress
        'listening': "🎧 <b>កំពុងស្ដាប់ និងវិភាគរលកសំឡេង...</b>\nសូមរង់ចាំបន្តិច...",
        'processing': "⏳ <b>កំពុងដំណើរការស្វែងរកបទភ្លេង...</b>",

        # Delivery Template (Matching REKI_MUSIC_BOT_BLUEPRINT.md)
        'song_found': (
            "🎶 <b>រកឃើញបទចម្រៀងហើយ!</b> 🎉\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎵 <b>ចំណងជើង:</b> <code>{title}</code>\n"
            "🎤 <b>អ្នកច្រៀង:</b> <code>{artist}</code>\n"
            "💿 <b>អាល់ប៊ុម:</b> <code>{album}</code>\n"
            "🏷️ <b>ប្រភេទ:</b> <code>{genre}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 <b>តំណភ្ជាប់ស្ដាប់កម្សាន្ត:</b>\n"
            "{links}\n\n"
            "📢 សូមគាំទ្រដោយចូល Join Channel @reki_anime_news"
        ),

        # Errors & Warnings
        'song_not_found': (
            "❌ <b>រកមិនឃើញបទចម្រៀងទេ!</b>\n\n"
            "សូមប្រាកដថាសំឡេងឮច្បាស់ល្អ (យ៉ាងតិច 3-5 វិនាទី) និងគ្មានសំឡេងរំខានខ្លាំងពេក។\n"
            "អ្នកអាចសាកល្បងថតសារជាថ្មីម្ដងទៀត! 🎧"
        ),
        'invalid_input': (
            "❌ <b>ទម្រង់មិនគាំទ្រទេ!</b>\n\n"
            "សូមផ្ញើជា <b>Voice Note</b>, <b>Audio file (MP3/M4A)</b>, <b>Video</b> ឬ Link វីដេអូ TikTok/Reels។\n"
            "ចុច /help ដើម្បីមើលការណែនាំ។"
        ),
        'file_too_large': (
            "❌ <b>File ធំពេក (លើស {max_size}MB)!</b>\n\n"
            "Telegram Bot API កម្រិតមិនឱ្យលើសពី {max_size}MB ឡើយ។\n"
            "សូមកាត់ជាកំណាត់ខ្លីត្រឹម 10-30 វិនាទី រួចផ្ញើមកម្ដងទៀត។"
        ),
        'error_general': (
            "⚠️ <b>មានបញ្ហាបច្ចេកទេសមួយបានកើតឡើង!</b>\n\n"
            "សូមព្យាយាមម្ដងទៀតនៅពេលបន្តិចទៀត។\n"
            "ប្រសិនបើនៅតែមិនដំណើរការ សូមទាក់ទងមកកាន់ @RekiReze"
        ),
        'maintenance_active': (
            "🛠 <b>ប្រព័ន្ធកំពុងស្ថិតក្នុងការថែទាំបណ្ដោះអាសន្ន!</b>\n\n"
            "យើងខ្ញុំកំពុងធ្វើការ Upgrade ប្រព័ន្ធដើម្បីបង្កើនល្បឿន និងប្រសិទ្ធភាព។\n"
            "សូមអភ័យទោសចំពោះការរំខាន។ សូមព្យាយាមម្ដងទៀតនៅពេលក្រោយ!\n"
            "ព័ត៌មានបន្ថែម: @reki_anime_news"
        ),
        'update_active': (
            "🚀 <b>ប្រព័ន្ធកំពុង Update និងតេស្តសាកល្បង!</b>\n\n"
            "Bot ត្រូវបានបើកដំណើរការសម្រាប់តែ Admin ប៉ុណ្ណោះនៅពេលនេះ។\n"
            "សូមរង់ចាំការប្រកាសបើកជាសាធារណៈឆាប់ៗនេះនៅលើ @reki_anime_news!"
        ),
        'admin_only': "⛔️ <b>មុខងារនេះសម្រាប់តែ Admin ប៉ុណ្ណោះ!</b>",
    },

    'en': {
        # Commands & Help
        'welcome': (
            "👋 <b>Hello {name}! Welcome to Reki Music Finder Bot!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "This bot identifies any song from your audio or video clips and provides complete track details instantly! 🎧⚡\n\n"
            "📥 <b>Supported Inputs:</b>\n"
            "  🎤 <b>Voice Note</b>: Record music playing around you (3-10s)\n"
            "  🎵 <b>Audio File</b>: Send MP3, M4A, or WAV audio files\n"
            "  📹 <b>Video</b>: Send video clips or Video Notes containing music\n"
            "  🔗 <b>TikTok & Reels</b>: Send video links to recognize background music\n\n"
            "👉 <b>How to use:</b> Just <b>send or forward Voice / Audio / Video / Link</b> right here!\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📌 <b>Commands:</b>\n"
            "• /start - Show this welcome message\n"
            "• /help - Detailed user guide\n"
            "• /about - Bot information & Developer\n"
            "• /language - Change language preference"
        ),
        'help': (
            "📖 <b>How to Use:</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "1️⃣ <b>Hear a song you like?</b> In a cafe, radio, or on your phone.\n"
            "2️⃣ <b>Send to Bot:</b>\n"
            "   • Record a <b>Voice Note</b> (at least 3-5 seconds)\n"
            "   • Or <b>Forward an audio/video message</b> from another chat\n"
            "   • Or <b>Copy Link</b> of a TikTok / IG Reel\n"
            "3️⃣ <b>Get Results:</b> The bot analyzes acoustic fingerprints, shows album cover art, song title, artist, album, and direct streaming links! 🚀\n\n"
            "⚠️ <b>Important Tips:</b>\n"
            "• Make sure the music is audible and avoid heavy background noise.\n"
            "• Minimum sample duration is 3 seconds."
        ),
        'about': (
            "ℹ️ <b>About Us</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 <b>Bot Name:</b> Reki Music Recognition Bot\n"
            "⚡ <b>Version:</b> 1.0 (Acoustic Fingerprint Engine)\n"
            "✨ <b>Key Features:</b>\n"
            "  • Fast and accurate acoustic recognition (Shazam Engine)\n"
            "  • Displays high-resolution cover artwork & full metadata\n"
            "  • Direct streaming links to YouTube, Spotify, and Apple Music\n"
            "  • Audio extraction from TikTok & Instagram links\n"
            "  • English and Khmer language support\n\n"
            "👨‍💻 <b>Developer & Contact:</b>\n"
            "  • <b>Developer:</b> @RekiReze\n"
            "  • <b>Official Channel:</b> @reki_anime_news\n"
            "  • <b>Platform:</b> Python, Telegram Bot API, SQLite\n\n"
            "❤️ Thank you for using and supporting Reki Bot Ecosystem!"
        ),
        'lang_select': (
            "🌐 <b>Please select your language / សូមជ្រើសរើសភាសារបស់អ្នក:</b>"
        ),
        'lang_changed': (
            "✅ Language changed to <b>🇬🇧 English</b> successfully!"
        ),

        # Status & Progress
        'listening': "🎧 <b>Listening & analyzing audio fingerprint...</b>\nPlease wait...",
        'processing': "⏳ <b>Identifying song...</b>",

        # Delivery Template (Matching REKI_MUSIC_BOT_BLUEPRINT.md)
        'song_found': (
            "🎶 <b>Song Recognized!</b> 🎉\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎵 <b>Title:</b> <code>{title}</code>\n"
            "🎤 <b>Artist:</b> <code>{artist}</code>\n"
            "💿 <b>Album:</b> <code>{album}</code>\n"
            "🏷️ <b>Genre:</b> <code>{genre}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 <b>Listen On:</b>\n"
            "{links}\n\n"
            "📢 Join channel: @reki_anime_news"
        ),

        # Errors & Warnings
        'song_not_found': (
            "❌ <b>Song not recognized!</b>\n\n"
            "Please ensure the audio is clear (at least 3-5 seconds long) and without excessive noise.\n"
            "Feel free to try recording again! 🎧"
        ),
        'invalid_input': (
            "❌ <b>Unsupported format!</b>\n\n"
            "Please send a <b>Voice Note</b>, <b>Audio file</b>, <b>Video clip</b>, or TikTok/Reels link.\n"
            "Press /help for more information."
        ),
        'file_too_large': (
            "❌ <b>File too large (exceeds {max_size}MB)!</b>\n\n"
            "Telegram Bot API limits file uploads to {max_size}MB.\n"
            "Please trim the audio/video to a 10-30 second snippet and try again."
        ),
        'error_general': (
            "⚠️ <b>A technical error occurred!</b>\n\n"
            "Please try again in a few moments.\n"
            "If the issue persists, contact @RekiReze"
        ),
        'maintenance_active': (
            "🛠 <b>Bot is currently under maintenance!</b>\n\n"
            "We are upgrading our servers for higher speed and better accuracy.\n"
            "Please check back soon!\n"
            "Updates: @reki_anime_news"
        ),
        'update_active': (
            "🚀 <b>System update in progress!</b>\n\n"
            "The bot is temporarily restricted to administrators for testing.\n"
            "Stay tuned for announcements on @reki_anime_news!"
        ),
        'admin_only': "⛔️ <b>This action is restricted to administrators!</b>",
    }
}


def t(key: str, lang: str = 'km', **kwargs: Any) -> str:
    """
    Retrieve localized string with optional keyword formatting.
    Falls back to Khmer ('km') then English ('en') if key is missing.
    """
    selected_lang = lang if lang in TRANSLATIONS else 'km'
    template = TRANSLATIONS[selected_lang].get(key)
    
    if template is None:
        template = TRANSLATIONS['km'].get(key)
    if template is None:
        template = TRANSLATIONS['en'].get(key, f"[{key}]")

    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template
