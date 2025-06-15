#AnyLink Downloader Bot.py - Fixed Version
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
import random
import time

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
        
        # Enhanced user agents with more variation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.0.0',
            'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
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
        """Get optimized yt-dlp options with anti-bot detection"""
        
        # Random user agent selection
        user_agent = random.choice(self.user_agents)
        
        # Base options with anti-detection measures
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
            'socket_timeout': 60,  # Increased timeout
            'retries': 5,  # More retries
            'fragment_retries': 5,
            'user_agent': user_agent,
            'referer': None,
            
            # Anti-bot detection headers
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            },
            
            # Additional anti-detection options
            'sleep_interval': random.uniform(1, 3),  # Random delay between requests
            'max_sleep_interval': 5,
            'sleep_interval_subtitles': random.uniform(0.5, 1.5),
            'extractor_args': {
                'youtube': {
                    'skip': ['hls', 'dash'],  # Skip problematic formats
                    'player_skip': ['configs'],  # Skip player config
                    'comment_sort': ['top'],
                    'max_comments': ['0'],  # Don't fetch comments
                }
            }
        }

        # Platform-specific configurations
        if platform == 'youtube':
            if attempt == 1:
                # First attempt: try for good quality but avoid problematic formats
                base_opts.update({
                    'format': 'best[height<=720][ext=mp4]/best[ext=mp4]/mp4/best',
                    'merge_output_format': 'mp4',
                    'prefer_ffmpeg': True,
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }]
                })
            elif attempt == 2:
                # Second attempt: lower quality, more compatible
                base_opts.update({
                    'format': 'best[height<=480]/worst[ext=mp4]/worst',
                    'prefer_ffmpeg': True
                })
            elif attempt == 3:
                # Third attempt: use alternative extractors
                base_opts.update({
                    'format': 'worst/best',
                    'prefer_insecure': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web'],
                            'skip': ['dash'],
                        }
                    }
                })
            else:
                # Last attempt: most basic settings
                base_opts.update({
                    'format': 'worst',
                    'prefer_insecure': True,
                    'no_check_certificate': True
                })
        
        elif platform == 'instagram':
            base_opts.update({
                'format': 'best[ext=mp4]/best',
                'http_headers': {
                    **base_opts['http_headers'],
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-Instagram-AJAX': '1',
                }
            })
        
        elif platform == 'tiktok':
            base_opts.update({
                'format': 'best[ext=mp4]/best',
                'http_headers': {
                    **base_opts['http_headers'],
                    'Referer': 'https://www.tiktok.com/',
                }
            })
        
        elif platform == 'facebook':
            base_opts.update({
                'format': 'best[ext=mp4]/best',
                'http_headers': {
                    **base_opts['http_headers'],
                    'Referer': 'https://www.facebook.com/',
                }
            })
        
        elif platform == 'twitter':
            base_opts.update({
                'format': 'best[ext=mp4]/best',
                'http_headers': {
                    **base_opts['http_headers'],
                    'Referer': 'https://twitter.com/',
                }
            })
        
        else:  # Unknown platform
            if attempt <= 2:
                base_opts.update({
                    'format': 'best[ext=mp4]/best',
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
🛡️ **Anti-Detection:** Advanced bot detection bypass

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

**Version:** 2.1.0 (Anti-Bot Fixed)
**Developer:** {self.developer_info['name']}
**Company:** {self.company_info['name']}

**Description:**
AnyLink Downloader is a versatile Telegram bot designed to simplify media downloads from various online platforms. This version includes advanced anti-bot detection bypass.

**Key Features:**
• Platform-specific download optimization
• Advanced anti-bot detection bypass
• Multiple retry strategies for better success
• Smart quality selection based on platform
• Enhanced error handling and user feedback
• Support for MP4 and other video formats
• User-friendly interface with inline keyboards

**Recent Improvements:**
• Fixed YouTube "Sign in to confirm you're not a bot" error
• Enhanced anti-detection measures
• Better Instagram and TikTok support
• Improved retry logic with random delays
• Platform-specific user agents and headers

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
        """Enhanced download function with anti-bot detection bypass"""
        user_id = update.effective_user.id
        platform = self.get_platform_from_url(url)
        
        logger.info(f"User {user_id} downloading from {platform}: {url}")
        
        # Show processing message
        processing_message = await update.message.reply_text(
            f"⏳ Processing your {platform.title()} request...\n"
            f"🔗 URL: `{url[:50]}{'...' if len(url) > 50 else ''}`\n\n"
            f"🎯 Platform detected: **{platform.title()}**\n"
            f"🛡️ Bypassing bot detection...\n"
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
            max_attempts = 5  # Increased attempts
            
            # Add initial delay to appear more human-like
            await asyncio.sleep(random.uniform(1, 3))
            
            # Try multiple configurations with enhanced anti-detection
            for attempt in range(1, max_attempts + 1):
                try:
                    await processing_message.edit_text(
                        f"📥 Downloading from {platform.title()} (Attempt {attempt}/{max_attempts})...\n"
                        f"🔗 URL: `{url[:50]}{'...' if len(url) > 50 else ''}`\n\n"
                        f"🛡️ Using advanced anti-detection (Method {attempt})\n"
                        f"⏳ This may take a few moments...",
                        parse_mode='Markdown'
                    )
                    
                    # Clean temp directory for new attempt
                    for file in os.listdir(temp_dir):
                        file_path_temp = os.path.join(temp_dir, file)
                        if os.path.isfile(file_path_temp):
                            os.remove(file_path_temp)
                    
                    # Add random delay between attempts
                    if attempt > 1:
                        delay = random.uniform(2, 5)
                        await asyncio.sleep(delay)
                    
                    # Get platform-specific options with anti-detection
                    ydl_opts = self.get_ydl_opts(temp_dir, platform, attempt)
                    
                    # Special handling for YouTube to avoid bot detection
                    if platform == 'youtube':
                        # Try to extract info first with minimal options
                        test_opts = {
                            'quiet': True,
                            'no_warnings': True,
                            'user_agent': random.choice(self.user_agents),
                            'socket_timeout': 30,
                            'extractor_args': {
                                'youtube': {
                                    'player_client': ['android', 'web'],
                                    'skip': ['dash', 'hls'],
                                }
                            }
                        }
                        
                        with yt_dlp.YoutubeDL(test_opts) as ydl:
                            try:
                                info = ydl.extract_info(url, download=False)
                                if not info:
                                    raise Exception("Could not extract video information")
                                logger.info(f"Successfully extracted info for YouTube video on attempt {attempt}")
                            except Exception as e:
                                logger.warning(f"Info extraction failed on attempt {attempt}: {str(e)}")
                                if attempt < max_attempts:
                                    continue
                                raise e
                    
                    # Perform the download with enhanced options
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
                    error_msg = str(e).lower()
                    logger.warning(f"Attempt {attempt} failed for {platform}: {str(e)}")
                    
                    # Check for specific YouTube bot detection errors
                    if platform == 'youtube' and ('sign in' in error_msg or 'bot' in error_msg):
                        logger.info(f"Bot detection encountered on attempt {attempt}, trying alternative method...")
                        # Continue to next attempt with different strategy
                        continue
                    
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
                f"🎯 Platform: {platform.title()}\n"
                f"✅ Anti-detection: Success!\n\n"
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
                     f"🤖 **Downloaded by AnyLink Downloader Bot**\n" \
                     f"🛡️ **Anti-Detection: Enabled**"
            
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
            
            # Enhanced error handling with specific solutions
            if platform == 'youtube':
                if "sign in" in error_message or "bot" in error_message:
                    specific_error = "🤖 YouTube detected bot activity - trying alternative methods"
                    suggestions = [
                        "• The bot is using advanced anti-detection methods",
                        "• Try again in a few minutes",
                        "• Some videos may be temporarily unavailable",
                        "• Make sure the video is public and not age-restricted"
                    ]
                elif "private" in error_message or "unavailable" in error_message:
                    specific_error = "🔒 YouTube: Video is private, unavailable, or deleted"
                    suggestions = [
                        "• Check if the video still exists",
                        "• Make sure the video is public",
                        "• Try a different YouTube video"
                    ]
                elif "live" in error_message:
                    specific_error = "📺 YouTube: Live streams cannot be downloaded"
                    suggestions = [
                        "• Wait for the live stream to end",
                        "• Try downloading after it becomes a regular video"
                    ]
                else:
                    specific_error = "📺 YouTube: Temporary access issue"
                    suggestions = [
                        "• The bot has advanced anti-detection enabled",
                        "• Try again in a few minutes",
                        "• Some videos may require special handling"
                    ]
            elif platform == 'instagram':
                if "private" in error_message or "login" in error_message:
                    specific_error = "🔒 Instagram: Account or post is private"
                    suggestions = [
                        "• Use direct Instagram post/reel links",
                        "• Make sure the account is public",
                        "• Try copying the link from Instagram web"
                    ]
                else:
                    specific_error = "📸 Instagram: Access issue"
                    suggestions = [
                        "• Use direct post or reel links",
                        "• Make sure the post is public",
                        "• Try again in a few minutes"
                    ]
            elif platform == 'tiktok':
                if "private" in error_message:
                    specific_error = "🔒 TikTok: Video is private or age-restricted"
                    suggestions = [
                        "• Try both tiktok.com and vm.tiktok.com links",
                        "• Make sure the video is public",
                        "• Some videos may be region-restricted"
                    ]
                else:
                    specific_error = "🎵 TikTok: Access issue"
                    suggestions = [
                        "• Try different URL formats",
                        "• Make sure the video is public",
                        "• Try again later"
                    ]
            elif platform == 'facebook':
                specific_error = "📘 Facebook: Most videos require login or are private"
                suggestions = [
                    "• Facebook videos are often restricted",
                    "• Try public Facebook pages",
                    "• YouTube links work better"
                ]
            elif platform == 'twitter':
                specific_error = "🐦 Twitter/X: Video access issue"
                suggestions = [
                    "• Make sure the tweet is public",
                    "• Try direct video links",
                    "• Some videos may be restricted"
                ]
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
                
                suggestions = [
                    "• YouTube links are most reliable",
                    "• Make sure the video is public",
                    "• Try again in a few minutes"
                ]
            
            suggestion_text = "\n".join(suggestions)
            
            await processing_message.edit_text(
                f"❌ **{platform.title()} Download Failed!**\n\n"
                f"{specific_error}\n\n"
                f"💡 **Suggestions:**\n"
                f"{suggestion_text}\n\n"
                f"🛡️ **Note:** This bot uses advanced anti-detection methods\n"
                f"✅ **Most reliable:** YouTube, public posts\n"
                f"⚠️ **May not work:** Private videos, login-required content\n\n"
                f"🔄 **Try again or contact support if issues persist**",
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

    def run(self):
        """Start the bot"""
        print("🚀 Starting AnyLink Downloader Bot (Anti-Bot Fixed Version)...")
        print(f"👨‍💻 Developer: {self.developer_info['name']}")
        print(f"🏢 Company: {self.company_info['name']}")
        print("🛡️ Anti-detection methods: ENABLED")
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
