#AnyLink Downloader Bot.py - Improved Version
import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
import tempfile
import shutil
import signal
import sys
import re
import json
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN', '7838776856:AAErH9mZQX1j29803t98hE9YFcab8fUm-gk')

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
        
        # Improved user agents for different platforms
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        self.setup_handlers()

    def setup_handlers(self):
        """Set up command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("about", self.about_command))
        self.application.add_handler(CommandHandler("contact", self.contact_command))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for URLs
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error("Exception while handling an update:", exc_info=context.error)
        
        # Notify user about the error
        if update and hasattr(update, 'effective_chat'):
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ An error occurred. Please try again or contact support if the problem persists."
                )
            except Exception:
                pass

    def is_valid_url(self, text):
        """Check if text contains a valid URL"""
        # More comprehensive URL detection
        url_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]+',
            r'(?:www\.)?(?:instagram\.com/(?:p|reel)/)[a-zA-Z0-9_-]+',
            r'(?:www\.)?(?:tiktok\.com/@[a-zA-Z0-9_.-]+/video/)[0-9]+',
            r'(?:www\.)?(?:facebook\.com/.+/videos/)[0-9]+',
            r'(?:www\.)?(?:twitter\.com|x\.com)/.+/status/[0-9]+',
            r'(?:vm\.tiktok\.com/)[a-zA-Z0-9]+',
            r'(?:www\.)?(?:twitch\.tv/videos/)[0-9]+'
        ]
        
        for pattern in url_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def get_platform_from_url(self, url):
        """Determine the platform from URL"""
        url_lower = url.lower()
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'tiktok.com' in url_lower or 'vm.tiktok.com' in url_lower:
            return 'tiktok'
        elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
            return 'facebook'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'twitch.tv' in url_lower:
            return 'twitch'
        elif 'reddit.com' in url_lower:
            return 'reddit'
        else:
            return 'unknown'

    def get_ydl_opts(self, temp_dir, platform='unknown', attempt=1):
        """Get optimized yt-dlp options based on platform and attempt"""
        base_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'ignoreerrors': True,
            'no_warnings': False,
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'embedsubs': False,
            'socket_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
            'user_agent': self.user_agents[attempt % len(self.user_agents)],
            'referer': None,
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        }

        # Platform-specific configurations
        if platform == 'youtube':
            if attempt == 1:
                base_opts.update({
                    'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4'
                })
            elif attempt == 2:
                base_opts.update({
                    'format': 'best[height<=480]/best',
                })
            else:
                base_opts.update({
                    'format': 'worst/best',
                })
        
        elif platform == 'instagram':
            base_opts.update({
                'format': 'best[ext=mp4]/best',
                'http_headers': {
                    **base_opts['http_headers'],
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            if attempt >= 2:
                base_opts['format'] = 'worst/best'
        
        elif platform == 'tiktok':
            base_opts.update({
                'format': 'best[ext=mp4]/best',
                'http_headers': {
                    **base_opts['http_headers'],
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                }
            })
        
        elif platform == 'facebook':
            base_opts.update({
                'format': 'best[ext=mp4]/best',
            })
        
        elif platform == 'twitter':
            base_opts.update({
                'format': 'best[ext=mp4]/best',
            })
        
        else:  # Unknown platform
            if attempt == 1:
                base_opts.update({
                    'format': 'best[ext=mp4]/best',
                })
            elif attempt == 2:
                base_opts.update({
                    'format': 'best[height<=480]/best',
                })
            else:
                base_opts.update({
                    'format': 'worst/best',
                })

        return base_opts

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_name = update.effective_user.first_name or "User"
        
        logger.info(f"User {update.effective_user.id} ({user_name}) started the bot")
        
        welcome_message = f"""
🎬 **Welcome to AnyLink Downloader Bot, {user_name}!** 🎬

I can help you download videos from various platforms including YouTube, Facebook, Instagram, TikTok, and many more!

**How to use:**
1. Send me any video URL
2. I'll download it automatically in the best available quality
3. Enjoy your video!

**Commands:**
/help - Show help information
/about - About this bot
/contact - Contact developer

Just send me a video URL to get started! 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("📋 Help", callback_data="help"),
             InlineKeyboardButton("ℹ️ About", callback_data="about")],
            [InlineKeyboardButton("📞 Contact", callback_data="contact")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            if update.message:
                await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
            elif update.callback_query:
                await update.callback_query.edit_message_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")

    def run(self):
        """Start the bot"""
        print("🚀 Starting AnyLink Downloader Bot (Improved Version)...")
        print(f"👨‍💻 Developer: {self.developer_info['name']}")
        print(f"🏢 Company: {self.company_info['name']}")
        print("📱 Bot is running... Press Ctrl+C to stop.")
        
        # Add post init callback
        self.application.post_init = self.post_init
        
        # Handle graceful shutdown
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal, stopping bot...")
            self.application.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the bot
        try:
            self.application.run_polling(
                drop_pending_updates=True,  # Ignore old messages
                allowed_updates=Update.ALL_TYPES
            )
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import yt_dlp
        import telegram
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install required packages:")
        print("pip install python-telegram-bot yt-dlp")
        sys.exit(1)
    
    bot = AnyLinkDownloaderBot()
    bot.run()
    logger.error(f"Error in start_command: {e}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🆘 **AnyLink Downloader Bot Help** 🆘

**Supported Platforms:**
✅ YouTube (youtube.com, youtu.be)
✅ Instagram (instagram.com/p/, instagram.com/reel/)
✅ TikTok (tiktok.com, vm.tiktok.com)
✅ Facebook (facebook.com/videos/)
✅ Twitter/X (twitter.com, x.com)
✅ Twitch (twitch.tv/videos/)
✅ And many more!

**How to Download:**
1. Copy the video URL from any supported platform
2. Send the URL to this bot
3. The bot will automatically download the video in the best quality available
4. Wait for the download to complete

**Features:**
📹 **Smart Quality Selection:** Adapts to each platform
🎵 **Multiple Formats:** Supports MP4 and other formats
⚡ **Fast Processing:** Optimized for each platform
🔄 **Retry Logic:** Multiple attempts for better success rate

**Tips:**
• For Instagram: Use direct post/reel links
• For TikTok: Both long and short URLs work
• For YouTube: Any video URL format works
• Private videos may not be downloadable
• Very long videos might take time to process

Need more help? Use /contact to reach the developer! 👨‍💻
        """
        
        keyboard = [
            [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            if update.message:
                await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
            elif update.callback_query:
                await update.callback_query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in help_command: {e}")

    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /about command"""
        about_text = f"""
ℹ️ **About AnyLink Downloader Bot** ℹ️

**Version:** 2.0.0 (Improved)
**Developer:** {self.developer_info['name']}
**Company:** {self.company_info['name']}

**Description:**
AnyLink Downloader is a versatile Telegram bot designed to simplify media downloads from various online platforms. This improved version features platform-specific optimizations and enhanced reliability.

**Key Features:**
• Platform-specific download optimization
• Multiple retry strategies for better success
• Smart quality selection based on platform
• Enhanced error handling and user feedback
• Support for MP4 and other video formats
• User-friendly interface with inline keyboards

**Recent Improvements:**
• Better Instagram and TikTok support
• Enhanced YouTube download reliability
• Platform-specific user agents and headers
• Improved error messages and troubleshooting

**Developed with ❤️ by KaRZMa Code**

For support and updates, use /contact to reach us!
        """
        
        keyboard = [
            [InlineKeyboardButton("📞 Contact Developer", callback_data="contact"),
             InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            if update.message:
                await update.message.reply_text(about_text, reply_markup=reply_markup, parse_mode='Markdown')
            elif update.callback_query:
                await update.callback_query.edit_message_text(about_text, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in about_command: {e}")

    async def contact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /contact command"""
        contact_text = f"""
📞 **Contact Information** 📞

**Developer:** {self.developer_info['name']}
📧 **Email:** {self.developer_info['email']}
📱 **WhatsApp:** {self.developer_info['whatsapp']}
💬 **Telegram:** {self.developer_info['telegram']}

**Company:** {self.company_info['name']}
📢 **Company Telegram:** [KaRZMa Code Channel]({self.company_info['telegram']})

**Social Media:**
🔗 [Facebook]({self.developer_info['facebook']})
📸 [Instagram]({self.developer_info['instagram']})
💼 [LinkedIn]({self.developer_info['linkedin']})

**Support:**
For technical support, bug reports, or feature requests, please contact us via WhatsApp or email.

**Business Inquiries:**
For business partnerships or custom development, reach out through our official channels.
        """
        
        keyboard = [
            [InlineKeyboardButton("💬 WhatsApp", url=f"https://wa.me/{self.developer_info['whatsapp'].replace('+', '')}")],
            [InlineKeyboardButton("📧 Email", url=f"mailto:{self.developer_info['email']}")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            if update.message:
                await update.message.reply_text(contact_text, reply_markup=reply_markup, parse_mode='Markdown', disable_web_page_preview=True)
            elif update.callback_query:
                await update.callback_query.edit_message_text(contact_text, reply_markup=reply_markup, parse_mode='Markdown', disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Error in contact_command: {e}")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        try:
            if data == "start":
                await self.start_command(update, context)
            elif data == "help":
                await self.help_command(update, context)
            elif data == "about":
                await self.about_command(update, context)
            elif data == "contact":
                await self.contact_command(update, context)
        except Exception as e:
            logger.error(f"Error in button_callback: {e}")
            await query.edit_message_text("❌ An error occurred. Please try again.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (URLs)"""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        logger.info(f"User {user_id} sent message: {message_text[:50]}...")
        
        # Check if message contains a URL
        if self.is_valid_url(message_text):
            await self.download_video(update, context, message_text)
        else:
            await update.message.reply_text(
                "🤔 Please send me a valid video URL from supported platforms like:\n\n"
                "✅ YouTube (youtube.com, youtu.be)\n"
                "✅ Instagram (instagram.com/p/, /reel/)\n"
                "✅ TikTok (tiktok.com, vm.tiktok.com)\n"
                "✅ Facebook (facebook.com/videos/)\n"
                "✅ Twitter/X (twitter.com, x.com)\n"
                "✅ And many more!\n\n"
                "Use /help to see the full list of supported platforms!"
            )

    async def download_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """Enhanced download function with platform-specific handling"""
        user_id = update.effective_user.id
        platform = self.get_platform_from_url(url)
        
        logger.info(f"User {user_id} downloading from {platform}: {url}")
        
        # Show processing message
        processing_message = await update.message.reply_text(
            f"⏳ Processing your {platform.title()} request...\n"
            f"🔗 URL: `{url[:50]}{'...' if len(url) > 50 else ''}`\n\n"
            f"🎯 Platform detected: **{platform.title()}**\n"
            f"Please wait while I download the video...",
            parse_mode='Markdown'
        )
        
        temp_dir = None
        try:
            # Create temporary directory for this download
            temp_dir = tempfile.mkdtemp()
            
            success = False
            title = "Unknown"
            duration = 0
            file_path = None
            max_attempts = 4
            
            # Try multiple configurations with platform-specific optimizations
            for attempt in range(1, max_attempts + 1):
                try:
                    await processing_message.edit_text(
                        f"📥 Downloading from {platform.title()} (Attempt {attempt}/{max_attempts})...\n"
                        f"🔗 URL: `{url[:50]}{'...' if len(url) > 50 else ''}`\n\n"
                        f"⏳ This may take a few moments...",
                        parse_mode='Markdown'
                    )
                    
                    # Clean temp directory for new attempt
                    for file in os.listdir(temp_dir):
                        file_path_temp = os.path.join(temp_dir, file)
                        if os.path.isfile(file_path_temp):
                            os.remove(file_path_temp)
                    
                    # Get platform-specific options
                    ydl_opts = self.get_ydl_opts(temp_dir, platform, attempt)
                    
                    # Add platform-specific extractors if needed
                    if platform == 'instagram':
                        # Try to extract info first to check if it's accessible
                        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                            try:
                                info = ydl.extract_info(url, download=False)
                                if not info:
                                    raise Exception("Could not extract video information")
                            except Exception as e:
                                if attempt < max_attempts:
                                    continue
                                raise e
                    
                    # Perform the download
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get('title', 'Unknown')
                        duration = info.get('duration', 0)
                        uploader = info.get('uploader', 'Unknown')
                        
                    # Check if file was downloaded
                    downloaded_files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
                    
                    if downloaded_files:
                        file_path = os.path.join(temp_dir, downloaded_files[0])
                        file_size = os.path.getsize(file_path)
                        
                        # Verify the file is not empty or corrupted
                        if file_size > 1024:  # At least 1KB
                            success = True
                            logger.info(f"Successfully downloaded from {platform} on attempt {attempt}")
                            break
                        else:
                            logger.warning(f"Downloaded file too small ({file_size} bytes) on attempt {attempt}")
                            
                except Exception as e:
                    logger.warning(f"Attempt {attempt} failed for {platform}: {str(e)}")
                    if attempt == max_attempts:
                        raise e
                    continue
            
            if not success or not file_path:
                raise Exception(f"All {max_attempts} download attempts failed. The video might be private, geo-blocked, or temporarily unavailable.")
            
            file_size = os.path.getsize(file_path)
            
            # Check file size (Telegram limit is 50MB for bots)
            if file_size > 50 * 1024 * 1024:  # 50MB
                await processing_message.edit_text(
                    f"❌ **File too large!**\n\n"
                    f"📁 File size: {file_size / (1024*1024):.1f} MB\n"
                    f"⚠️ Telegram limit: 50 MB\n\n"
                    f"The video from {platform.title()} is too large to send via Telegram.\n"
                    f"Please try with a shorter video or different quality.",
                    parse_mode='Markdown'
                )
                return
            
            # Update status
            await processing_message.edit_text(
                f"📤 Uploading to Telegram...\n"
                f"📁 **{title[:30]}{'...' if len(title) > 30 else ''}**\n"
                f"📊 Size: {file_size / (1024*1024):.1f} MB\n"
                f"🎯 Platform: {platform.title()}\n\n"
                f"⏳ Almost done...",
                parse_mode='Markdown'
            )
            
            # Prepare caption with platform info
            duration_text = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
            caption = f"✅ **Download Complete!**\n\n" \
                     f"📁 **Title:** {title[:50]}{'...' if len(title) > 50 else ''}\n" \
                     f"🎯 **Platform:** {platform.title()}\n" \
                     f"⏱️ **Duration:** {duration_text}\n" \
                     f"📊 **Size:** {file_size / (1024*1024):.1f} MB\n\n" \
                     f"🤖 **Downloaded by AnyLink Downloader Bot**"
            
            # Send the video
            with open(file_path, 'rb') as file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=file,
                    caption=caption,
                    parse_mode='Markdown',
                    supports_streaming=True
                )
            
            # Delete the processing message
            await processing_message.delete()
                
            logger.info(f"Successfully processed {platform} download for user {user_id}")
                
        except Exception as e:
            logger.error(f"Download error for user {user_id} from {platform}: {str(e)}")
            error_message = str(e).lower()
            
            # Provide platform-specific error messages
            if platform == 'instagram':
                if "private" in error_message or "login" in error_message:
                    specific_error = "🔒 Instagram: This account or post is private"
                elif "not found" in error_message:
                    specific_error = "❌ Instagram: Post not found or deleted"
                else:
                    specific_error = "📸 Instagram: Try using direct post/reel links"
            elif platform == 'tiktok':
                if "private" in error_message:
                    specific_error = "🔒 TikTok: This video is private or age-restricted"
                elif "not available" in error_message:
                    specific_error = "❌ TikTok: Video not available in this region"
                else:
                    specific_error = "🎵 TikTok: Try both long and short URL formats"
            elif platform == 'youtube':
                if "private" in error_message:
                    specific_error = "🔒 YouTube: This video is private or unlisted"
                elif "live" in error_message:
                    specific_error = "📺 YouTube: Live streams cannot be downloaded"
                else:
                    specific_error = "📺 YouTube: Video may be geo-blocked or removed"
            elif platform == 'facebook':
                specific_error = "📘 Facebook: Most videos require login or are private"
            elif platform == 'twitter':
                specific_error = "🐦 Twitter/X: Video may be private or deleted"
            else:
                if "login" in error_message or "private" in error_message:
                    specific_error = "🔒 This video requires login or is private"
                elif "rate" in error_message or "limit" in error_message:
                    specific_error = "⏱️ Rate limit reached - please try again later"
                elif "geo" in error_message or "country" in error_message:
                    specific_error = "🌍 Video not available in this region"
                elif "not available" in error_message:
                    specific_error = "❌ Video not available or removed"
                else:
                    specific_error = f"🚫 {str(e)[:80]}{'...' if len(str(e)) > 80 else ''}"
            
            # Platform-specific suggestions
            suggestions = []
            if platform == 'instagram':
                suggestions = [
                    "• Use direct Instagram post or reel links",
                    "• Make sure the account is public",
                    "• Try copying the link from Instagram web"
                ]
            elif platform == 'tiktok':
                suggestions = [
                    "• Try both tiktok.com and vm.tiktok.com links",
                    "• Make sure the video is public",
                    "• Some TikTok videos may be region-restricted"
                ]
            elif platform == 'youtube':
                suggestions = [
                    "• YouTube links are most reliable",
                    "• Make sure the video is public",
                    "• Try copying the link from YouTube directly"
                ]
            else:
                suggestions = [
                    "• Try YouTube links (most reliable)",
                    "• Make sure the video is public/non-private",
                    "• Check if the URL is correct and complete"
                ]
            
            suggestion_text = "\n".join(suggestions)
            
            await processing_message.edit_text(
                f"❌ **{platform.title()} Download Failed!**\n\n"
                f"{specific_error}\n\n"
                f"💡 **Suggestions:**\n"
                f"{suggestion_text}\n"
                f"• Wait a few minutes and try again\n\n"
                f"✅ **Most reliable:** YouTube, public posts\n"
                f"⚠️ **May not work:** Private videos, login-required content",
                parse_mode='Markdown'
            )
        
        finally:
            # Clean up
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    async def post_init(self, application: Application):
        """Called after the bot is initialized"""
        logger.info("Bot initialized successfully!")
        
        # Test bot connection
        try:
            bot_info = await application.bot.get_me()
            logger.info(f"Bot @{bot_info.username} is ready!")
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")
            print(f"❌ Failed to get bot info: {e}")
