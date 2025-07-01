#AnyLink Downloader Bot.py - v2.2 (Enhanced Anti-Bot)
import os
import asyncio
import logging
import sys
import re
import random
import time
import tempfile
import shutil
import signal
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

# --- Configuration ---

# Configure logging to output to the console (best for services like Railway)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Get BOT_TOKEN from environment variables. Exit if not found.
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.critical("FATAL: BOT_TOKEN environment variable is not set.")
    sys.exit(1)

# Get optional YouTube cookie file path from environment variables
# This is an advanced feature for the developer to bypass stubborn blocks.
YOUTUBE_COOKIE_FILE = os.getenv('YOUTUBE_COOKIE_FILE', None)
if YOUTUBE_COOKIE_FILE and not os.path.exists(YOUTUBE_COOKIE_FILE):
    logger.warning(f"YouTube cookie file specified but not found at: {YOUTUBE_COOKIE_FILE}")
    YOUTUBE_COOKIE_FILE = None


class AnyLinkDownloaderBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Developer and company info
        self.developer_info = {
            'name': 'Mohammed Salem Alwosabi',
            'email': 'm.salem.alwosabi@gmail.com',
            'whatsapp': '+967739003665',
            'telegram': '@MohammedAlwosabi',
            'facebook': 'https://www.facebook.com/share/1EetzPibZt/',
            'instagram': 'https://www.instagram.com/m.salem_hy',
            'linkedin': 'https://www.linkedin.com/in/mohammed-salem-ali-alwosabi-842757321'
        }
        
        self.company_info = {
            'name': 'KaRZMa Code',
            'telegram': 'https://t.me/KaRZMa_Code',
            'facebook': 'https://www.facebook.com/profile.php?id=61551057515420',
            'instagram': 'https://instagram.com/karzma_co.ms'
        }
        
        # Enhanced user agents with more variation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        ]
        
        self.setup_handlers()

    def setup_handlers(self):
        """Set up command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("about", self.about_command))
        self.application.add_handler(CommandHandler("contact", self.contact_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error_handler)

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Log Errors caused by Updates."""
        logger.error("Exception while handling an update:", exc_info=context.error)
        if update and hasattr(update, 'effective_chat'):
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ An unexpected error occurred. The developer has been notified. Please try again later."
                )
            except Exception as e:
                logger.error(f"Failed to send error message to user: {e}")

    def is_valid_url(self, text):
        """Check if text contains a valid URL using a more robust regex"""
        # This regex is quite broad to catch URLs in various formats.
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        return re.search(url_pattern, text) is not None

    def get_platform_from_url(self, url):
        """Determine the platform from URL"""
        hostname = urlparse(url).hostname.lower().replace('www.', '')
        if 'youtube.com' in hostname or 'youtu.be' in hostname:
            return 'youtube'
        if 'instagram.com' in hostname:
            return 'instagram'
        if 'tiktok.com' in hostname:
            return 'tiktok'
        if 'facebook.com' in hostname or 'fb.watch' in hostname:
            return 'facebook'
        if 'twitter.com' in hostname or 'x.com' in hostname:
            return 'twitter'
        if 'twitch.tv' in hostname:
            return 'twitch'
        if 'reddit.com' in hostname:
            return 'reddit'
        return 'unknown'

    def get_ydl_opts(self, temp_dir, platform='unknown', attempt=1):
        """Get yt-dlp options with an enhanced, multi-layered anti-bot strategy."""
        user_agent = random.choice(self.user_agents)
        
        # Base options with common anti-detection measures
        base_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'ignoreerrors': True,
            'no_warnings': False,
            'socket_timeout': 60,
            'retries': 3, # yt-dlp internal retries
            'fragment_retries': 3,
            'user_agent': user_agent,
            'http_headers': {
                'Accept-Language': 'en-US,en;q=0.5'
            },
            'sleep_interval': random.uniform(1, 4), # Random delay between requests
            'max_sleep_interval': 6,
        }

        # --- Platform-specific configurations ---

        if platform == 'youtube':
            # This dictionary will be updated based on the attempt number
            yt_opts = {
                'extractor_args': {
                    'youtube': {
                        'skip': ['hls', 'dash'],
                        'player_skip': ['configs'],
                        'max_comments': ['0'],
                    }
                }
            }
            if attempt == 1: # Standard web client, good quality
                yt_opts['format'] = 'best[height<=720][ext=mp4]/best[ext=mp4]/mp4/best'
                yt_opts['extractor_args']['youtube']['player_client'] = ['web']
            elif attempt == 2: # Android client, slightly lower quality
                yt_opts['format'] = 'best[height<=480][ext=mp4]/best[ext=mp4]/mp4/best'
                yt_opts['extractor_args']['youtube']['player_client'] = ['android']
            elif attempt == 3: # iOS client, good quality
                yt_opts['format'] = 'best[height<=720][ext=mp4]/best[ext=mp4]/mp4/best'
                yt_opts['extractor_args']['youtube']['player_client'] = ['ios']
            elif attempt == 4: # Last resort: insecure, worst quality
                yt_opts['format'] = 'worst[ext=mp4]/worst'
                yt_opts['prefer_insecure'] = True
            elif attempt == 5: # The final attempt with everything thrown at it
                yt_opts['format'] = 'worst/best'
                yt_opts['prefer_insecure'] = True
                yt_opts['no_check_certificate'] = True
                # Use cookies if provided via environment variable (for developer use)
                if YOUTUBE_COOKIE_FILE:
                    yt_opts['cookiefile'] = YOUTUBE_COOKIE_FILE
                    logger.info("Attempt 5: Using YouTube cookie file for download.")
                else:
                    logger.warning("Attempt 5: No cookie file found. This attempt may fail.")
            
            base_opts.update(yt_opts)
        
        else: # Generic settings for other platforms
            base_opts['format'] = 'best[ext=mp4]/best'

        return base_opts

    # --- Command Handlers (start, help, about, contact) are unchanged ---
    # (Keeping them here for completeness, no modifications needed)
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_name = update.effective_user.first_name or "User"
        logger.info(f"User {update.effective_user.id} ({user_name}) started the bot")
        welcome_message = f"""🎬 **Welcome to AnyLink Downloader Bot, {user_name}!** 🎬\n\nI can help you download videos from various platforms including YouTube, Facebook, Instagram, TikTok, and many more!\n\n**How to use:**\n1. Send me any video URL\n2. I'll download it automatically\n3. Enjoy your video!\n\n**Commands:**\n/help - Show help information\n/about - About this bot\n/contact - Contact developer\n\nJust send me a video URL to get started! 🚀"""
        keyboard = [[InlineKeyboardButton("📋 Help", callback_data="help"), InlineKeyboardButton("ℹ️ About", callback_data="about")], [InlineKeyboardButton("📞 Contact", callback_data="contact")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        target = update.message or update.callback_query
        await target.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown') if isinstance(target, Update.message_class) else await target.edit_message_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """🆘 **AnyLink Downloader Bot Help** 🆘\n\n**Supported Platforms:**\n✅ YouTube\n✅ Instagram\n✅ TikTok\n✅ Facebook\n✅ Twitter/X\n✅ And many more!\n\n**How to Download:**\n1. Copy the video URL from any supported platform\n2. Send the URL to this bot\n3. The bot will automatically download the video\n\n**Features:**\n📹 **Smart Quality Selection**\n⚡ **Fast Processing**\n🔄 **Advanced Retry Logic**\n🛡️ **Enhanced Anti-Detection**\n\nNeed more help? Use /contact to reach the developer! 👨‍💻"""
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        target = update.message or update.callback_query
        await target.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown') if isinstance(target, Update.message_class) else await target.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        about_text = f"""ℹ️ **About AnyLink Downloader Bot** ℹ️\n\n**Version:** 2.2.0 (Enhanced Anti-Bot)\n**Developer:** {self.developer_info['name']}\n**Company:** {self.company_info['name']}\n\nThis bot uses advanced techniques to download videos from many platforms, including a multi-layered approach to bypass bot detection.\n\n**Developed with ❤️ by KaRZMa Code**"""
        keyboard = [[InlineKeyboardButton("📞 Contact Developer", callback_data="contact"), InlineKeyboardButton("🏠 Main Menu", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        target = update.message or update.callback_query
        await target.reply_text(about_text, reply_markup=reply_markup, parse_mode='Markdown') if isinstance(target, Update.message_class) else await target.edit_message_text(about_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def contact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        contact_text = f"""📞 **Contact Information** 📞\n\n**Developer:** {self.developer_info['name']}\n📧 **Email:** {self.developer_info['email']}\n📱 **WhatsApp:** {self.developer_info['whatsapp']}\n💬 **Telegram:** {self.developer_info['telegram']}\n\n**Company:** {self.company_info['name']}\n📢 **Company Telegram:** [KaRZMa Code Channel]({self.company_info['telegram']})"""
        keyboard = [[InlineKeyboardButton("💬 WhatsApp", url=f"https://wa.me/{self.developer_info['whatsapp'].replace('+', '')}")], [InlineKeyboardButton("📧 Email", url=f"mailto:{self.developer_info['email']}")], [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        target = update.message or update.callback_query
        await target.reply_text(contact_text, reply_markup=reply_markup, parse_mode='Markdown', disable_web_page_preview=True) if isinstance(target, Update.message_class) else await target.edit_message_text(contact_text, reply_markup=reply_markup, parse_mode='Markdown', disable_web_page_preview=True)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        command_map = {
            "start": self.start_command,
            "help": self.help_command,
            "about": self.about_command,
            "contact": self.contact_command,
        }
        if query.data in command_map:
            await command_map[query.data](update, context)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (URLs)"""
        message_text = update.message.text.strip()
        if self.is_valid_url(message_text):
            # Extract the first URL found in the message
            url = re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_text).group(0)
            await self.download_video(update, context, url)
        else:
            await update.message.reply_text("🤔 Please send me a valid video URL.")

    async def download_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """Enhanced download function with multi-layered anti-bot bypass."""
        platform = self.get_platform_from_url(url)
        logger.info(f"User {update.effective_user.id} starting download from {platform}: {url}")
        
        processing_message = await update.message.reply_text(
            f"⏳ Processing your {platform.title()} request...", parse_mode='Markdown'
        )
        
        temp_dir = tempfile.mkdtemp()
        try:
            success = False
            file_path = None
            max_attempts = 5
            last_error = "Unknown error"
            
            for attempt in range(1, max_attempts + 1):
                try:
                    await processing_message.edit_text(
                        f"📥 Downloading from {platform.title()} (Attempt {attempt}/{max_attempts})...\n"
                        f"🛡️ Using anti-detection method #{attempt}",
                        parse_mode='Markdown'
                    )
                    
                    # Clean temp directory for new attempt
                    for f in os.listdir(temp_dir):
                        os.remove(os.path.join(temp_dir, f))
                    
                    if attempt > 1: await asyncio.sleep(random.uniform(2, 5))
                    
                    ydl_opts = self.get_ydl_opts(temp_dir, platform, attempt)
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        
                    downloaded_files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
                    
                    if downloaded_files:
                        file_path = os.path.join(temp_dir, downloaded_files[0])
                        if os.path.getsize(file_path) > 1024:
                            success = True
                            logger.info(f"Successfully downloaded on attempt {attempt}")
                            break
                        else:
                            last_error = "Downloaded file was empty."
                            logger.warning(f"Attempt {attempt} resulted in an empty file.")
                    else:
                        last_error = "No file was downloaded."
                        logger.warning(f"Attempt {attempt} did not produce a file.")
                        
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"Attempt {attempt} failed for {platform}: {last_error}")
                    if attempt == max_attempts:
                        raise e # Re-raise the last error if all attempts fail
            
            if not success or not file_path:
                raise Exception(f"All {max_attempts} download attempts failed. Last error: {last_error}")
            
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > 49:
                await processing_message.edit_text(f"❌ **File too large!** ({file_size_mb:.1f} MB). Telegram's limit is 50 MB.")
                return
            
            await processing_message.edit_text("📤 Uploading to Telegram...")
            
            # Use info from the last successful download
            title = info.get('title', 'Unknown Title')
            duration = info.get('duration', 0)
            duration_text = f"{duration//60}:{duration%60:02d}" if duration else "N/A"
            caption = f"✅ **{title[:60]}...**\n\n" \
                      f"🎯 **Platform:** {platform.title()} | ⏱️ **Duration:** {duration_text}\n\n" \
                      f"🤖 Downloaded by @{context.bot.username}"
            
            with open(file_path, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption=caption,
                    parse_mode='Markdown',
                    supports_streaming=True
                )
            await processing_message.delete()
                
        except Exception as e:
            logger.error(f"Final download error for user {update.effective_user.id}: {str(e)}")
            error_message = str(e).lower()
            
            final_error_text = "❌ **Download Failed!**\n\n"
            if 'sign in to confirm' in error_message or 'not a bot' in error_message:
                final_error_text += "🤖 **Reason:** YouTube is blocking the download, suspecting bot activity. This is a common issue as their security is very high.\n\n💡 **What to do:** Please try a different video or try this one again later. Some videos are more protected than others."
            elif "private" in error_message or "unavailable" in error_message:
                final_error_text += f"🔒 **Reason:** The video on {platform.title()} is private, has been deleted, or is unavailable."
            elif "geo" in error_message or "country" in error_message:
                final_error_text += f"🌍 **Reason:** This video is geo-restricted and not available for download from the bot's server location."
            else:
                final_error_text += f"🔧 **Reason:** An unexpected technical issue occurred. The developer has been notified.\n\n`Error: {str(e)[:100]}`"
            
            await processing_message.edit_text(final_error_text, parse_mode='Markdown')
        
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    async def post_init(self, application: Application):
        """Called after the bot is initialized"""
        bot_info = await application.bot.get_me()
        logger.info(f"Bot @{bot_info.username} (v2.2) is initialized and ready!")

    def run(self):
        """Start the bot"""
        logger.info("🚀 Starting AnyLink Downloader Bot (v2.2 Enhanced Anti-Bot)...")
        self.application.post_init = self.post_init
        
        # Handle graceful shutdown on Ctrl+C
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal, stopping bot...")
            # This is a simplified shutdown. For production, you might want more complex cleanup.
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = AnyLinkDownloaderBot()
    bot.run()
