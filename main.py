#AnyLink Downloader Bot.py
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
from datetime import datetime

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
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        return url_pattern.search(text) is not None

    def extract_url_from_text(self, text):
        """Extract the first URL from text"""
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        match = url_pattern.search(text)
        return match.group(0) if match else None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_name = update.effective_user.first_name or "User"
        
        logger.info(f"User {update.effective_user.id} ({user_name}) started the bot")
        
        welcome_message = f"""
🎬 **Welcome to AnyLink Downloader Bot, {user_name}!** 🎬

I can help you download videos from various platforms including YouTube, Facebook, Instagram, TikTok, and many more!

**How to use:**
1. 📋 Copy any video URL from supported platforms
2. 📤 Send the URL to me in this chat
3. ⏳ I'll process and download the video
4. 📱 You'll receive the video file directly in this chat
5. 💾 Tap and hold the video to save it to your device

**Supported formats:** MP4 (up to 50MB due to Telegram limits)

**Commands:**
/help - Show detailed help
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
• 🎥 YouTube (videos, shorts)
• 📘 Facebook (public videos)
• 📸 Instagram (public posts, reels)
• 🐦 Twitter/X (videos)
• 🎵 TikTok (public videos)
• 📹 Vimeo
• 🎬 Dailymotion
• And many more platforms!

**How to Download:**
1. 📋 Copy the video URL from any supported platform
2. 📤 Paste and send the URL to this bot
3. ⏳ Wait while the bot processes your request
4. 📱 The video will be sent directly to this chat
5. 💾 Long press the video to download to your device

**Download Process:**
📥 **Processing:** Bot analyzes the URL
🔄 **Downloading:** Bot fetches the video
📤 **Uploading:** Video is sent to your chat
✅ **Complete:** Ready to save on your device

**Features:**
📹 **Smart Quality:** Automatically selects best available quality
🎵 **MP4 Format:** Compatible with all devices
⚡ **Fast Processing:** Quick downloads and uploads
📊 **File Info:** Shows title, duration, and size

**Limitations:**
🔒 Private videos cannot be downloaded
👤 Login-required content not supported
📏 Maximum file size: 50MB (Telegram limit)
🌍 Some geo-restricted content may not work

**Tips for Better Results:**
✅ Use public video URLs
✅ YouTube links work best
✅ Ensure the video is still available
✅ Shorter videos process faster

Need help? Use /contact to reach the developer! 👨‍💻
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

**Version:** 2.0.0
**Developer:** {self.developer_info['name']}
**Company:** {self.company_info['name']}

**Description:**
AnyLink Downloader is a versatile Telegram bot designed to simplify media downloads from various online platforms. Send any supported video URL and receive the video file directly in your chat for easy downloading.

**Key Features:**
🎯 **Direct Download:** Videos sent straight to your chat
📱 **Easy Saving:** Long press to save videos to your device
🔄 **Smart Processing:** Multiple quality fallback options
📊 **File Information:** Shows title, duration, and file size
🛡️ **Error Handling:** Clear error messages and suggestions
⚡ **Fast Performance:** Optimized for quick processing

**How It Works:**
1. You send a video URL
2. Bot downloads the video from the platform
3. Video is uploaded directly to your Telegram chat
4. You can save it to your device with a long press

**Technical Details:**
🔧 Built with Python and python-telegram-bot
📦 Uses yt-dlp for video extraction
☁️ Processes videos in temporary storage
🗑️ Automatic cleanup after processing

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

**Support Types:**
🔧 Technical support and bug reports
💡 Feature requests and suggestions
🤝 Business partnerships and collaborations
⚙️ Custom bot development services

**Response Time:**
📧 Email: Within 24 hours
📱 WhatsApp: Within 12 hours
💬 Telegram: Within 6 hours

Feel free to reach out for any assistance! 😊
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
            url = self.extract_url_from_text(message_text)
            await self.download_video(update, context, url)
        else:
            await update.message.reply_text(
                "🤔 **Please send me a valid video URL!**\n\n"
                "📋 **How to get a video URL:**\n"
                "1. Go to the video on any supported platform\n"
                "2. Tap the Share button\n"
                "3. Copy the link/URL\n"
                "4. Paste it here and send\n\n"
                "🎬 **Supported platforms:** YouTube, Facebook, Instagram, TikTok, Twitter, and more!\n\n"
                "💡 Use /help to see the complete list of supported platforms.",
                parse_mode='Markdown'
            )

    async def download_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """Download video and send it back to user in the chat"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "User"
        
        logger.info(f"User {user_id} ({user_name}) downloading: {url}")
        
        # Show initial processing message
        processing_message = await update.message.reply_text(
            f"🎬 **Processing Video Download**\n\n"
            f"👤 **User:** {user_name}\n"
            f"🔗 **URL:** `{url[:60]}{'...' if len(url) > 60 else ''}`\n"
            f"⏰ **Started:** {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"⏳ **Status:** Analyzing video...\n"
            f"📥 Please wait while I fetch your video...",
            parse_mode='Markdown'
        )
        
        temp_dir = None
        try:
            # Create temporary directory for this download
            temp_dir = tempfile.mkdtemp()
            
            # Multiple configuration attempts with different strategies
            config_attempts = [
                {
                    'name': 'High Quality (720p)',
                    'opts': {
                        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                        'noplaylist': True,
                        'ignoreerrors': True,
                        'no_warnings': True,
                        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[ext=mp4]',
                        'merge_output_format': 'mp4',
                        'extract_flat': False,
                        'writesubtitles': False,
                        'writeautomaticsub': False,
                        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    }
                },
                {
                    'name': 'Medium Quality (480p)',
                    'opts': {
                        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                        'noplaylist': True,
                        'ignoreerrors': True,
                        'no_warnings': True,
                        'format': 'best[height<=480][ext=mp4]/best[height<=480]/best[ext=mp4]',
                        'merge_output_format': 'mp4',
                        'extract_flat': False,
                        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                },
                {
                    'name': 'Basic Quality',
                    'opts': {
                        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                        'noplaylist': True,
                        'ignoreerrors': True,
                        'no_warnings': True,
                        'format': 'worst[ext=mp4]/worst/best[ext=mp4]/best',
                        'extract_flat': False
                    }
                }
            ]
            
            success = False
            title = "Unknown Video"
            duration = 0
            uploader = "Unknown"
            view_count = 0
            
            # Try each configuration
            for attempt_num, attempt in enumerate(config_attempts, 1):
                try:
                    await processing_message.edit_text(
                        f"🎬 **Processing Video Download**\n\n"
                        f"👤 **User:** {user_name}\n"
                        f"🔗 **URL:** `{url[:60]}{'...' if len(url) > 60 else ''}`\n"
                        f"⏰ **Started:** {datetime.now().strftime('%H:%M:%S')}\n\n"
                        f"📥 **Status:** Downloading ({attempt['name']})...\n"
                        f"🔄 **Attempt:** {attempt_num}/{len(config_attempts)}\n"
                        f"⏳ This may take a few moments depending on video size...",
                        parse_mode='Markdown'
                    )
                    
                    # Clean temp directory for new attempt
                    for file in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    
                    with yt_dlp.YoutubeDL(attempt['opts']) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get('title', 'Unknown Video')
                        duration = info.get('duration', 0)
                        uploader = info.get('uploader', 'Unknown')
                        view_count = info.get('view_count', 0)
                        
                    # Check if file was downloaded
                    downloaded_files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
                    
                    if downloaded_files:
                        success = True
                        logger.info(f"Successfully downloaded with {attempt['name']} configuration")
                        break
                        
                except Exception as e:
                    logger.warning(f"Failed with {attempt['name']} configuration: {str(e)}")
                    if attempt_num < len(config_attempts):
                        await asyncio.sleep(2)  # Brief pause between attempts
                    continue
            
            if not success:
                raise Exception("All download attempts failed. The video might be private, geo-blocked, or from an unsupported platform.")
            
            # Find the downloaded file
            downloaded_files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            
            if not downloaded_files:
                raise Exception("No file was downloaded despite successful extraction")
            
            file_path = os.path.join(temp_dir, downloaded_files[0])
            file_size = os.path.getsize(file_path)
            
            # Check file size (Telegram limit is 50MB for bots)
            if file_size > 50 * 1024 * 1024:  # 50MB
                await processing_message.edit_text(
                    f"❌ **File Too Large for Telegram!**\n\n"
                    f"📁 **Video Title:** {title[:50]}{'...' if len(title) > 50 else ''}\n"
                    f"📊 **File Size:** {file_size / (1024*1024):.1f} MB\n"
                    f"⚠️ **Telegram Limit:** 50 MB maximum\n\n"
                    f"💡 **Suggestion:** Try downloading a shorter video or lower quality version.\n"
                    f"🎬 **Platform:** Try using the platform's built-in download feature for large files.",
                    parse_mode='Markdown'
                )
                return
            
            # Check if file is valid (minimum 1KB)
            if file_size < 1024:
                raise Exception("Downloaded file is too small or corrupted")
            
            # Update status for upload
            await processing_message.edit_text(
                f"🎬 **Uploading Video to Chat**\n\n" 
                f"👤 **User:** {user_name}\n"
                f"📁 **Title:** {title[:40]}{'...' if len(title) > 40 else ''}\n"
                f"👨‍💻 **Uploader:** {uploader[:30]}{'...' if len(uploader) > 30 else ''}\n"
                f"📊 **Size:** {file_size / (1024*1024):.1f} MB\n\n"
                f"📤 **Status:** Uploading to Telegram...\n"
                f"⏳ Almost ready for download!",
                parse_mode='Markdown'
            )
            
            # Prepare detailed caption
            duration_text = f"{duration//60}:{duration%60:02d}" if duration > 0 else "Unknown"
            view_text = f"{view_count:,}" if view_count > 0 else "Unknown"
            
            caption = f"✅ **Download Complete!**\n\n" \
                     f"📁 **Title:** {title[:100]}{'...' if len(title) > 100 else ''}\n" \
                     f"👨‍💻 **Channel:** {uploader[:50]}{'...' if len(uploader) > 50 else ''}\n" \
                     f"⏱️ **Duration:** {duration_text}\n" \
                     f"👀 **Views:** {view_text}\n" \
                     f"📊 **Size:** {file_size / (1024*1024):.1f} MB\n\n" \
                     f"💾 **To Save:** Long press the video and select 'Save to Gallery'\n\n" \
                     f"🤖 **Downloaded by @AnyLinkDownloaderBot**\n" \
                     f"🏢 **By KaRZMa Code**"
            
            # Send the video file to the chat
            with open(file_path, 'rb') as file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=file,
                    caption=caption,
                    parse_mode='Markdown',
                    supports_streaming=True,
                    width=1280,  # Optional: set video dimensions
                    height=720,
                    duration=duration if duration > 0 else None
                )
            
            # Send success message with instructions
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🎉 **Video Successfully Delivered!**\n\n"
                     f"📱 **Your video is now in this chat!**\n\n"
                     f"💾 **To download to your device:**\n"
                     f"• **Mobile:** Long press the video → Save to Gallery\n"
                     f"• **Desktop:** Right click the video → Save video as...\n\n"
                     f"🔄 **Want another video?** Just send me another URL!\n"
                     f"📋 **Need help?** Use /help for more information",
                parse_mode='Markdown'
            )
            
            # Delete the processing message
            try:
                await processing_message.delete()
            except:
                pass  # Message might already be deleted
                
            logger.info(f"Successfully processed and delivered video for user {user_id} ({user_name})")
                
        except Exception as e:
            logger.error(f"Download error for user {user_id}: {str(e)}")
            error_message = str(e).lower()
            
            # Provide specific error messages based on the error type
            if any(keyword in error_message for keyword in ["login", "private", "authentication"]):
                specific_error = "🔒 **Private Content**\nThis video requires login or is set to private"
                suggestion = "Try a public video from the same platform"
            elif any(keyword in error_message for keyword in ["rate", "limit", "throttle"]):
                specific_error = "⏱️ **Rate Limited**\nToo many requests - please wait before trying again"
                suggestion = "Wait 5-10 minutes and try again"
            elif any(keyword in error_message for keyword in ["geo", "country", "region", "blocked"]):
                specific_error = "🌍 **Geo-Restricted**\nVideo not available in this region"
                suggestion = "Try a different video or use a VPN"
            elif any(keyword in error_message for keyword in ["not available", "removed", "deleted"]):
                specific_error = "❌ **Video Unavailable**\nVideo has been removed or is no longer available"
                suggestion = "Check if the video URL is still valid"
            elif "instagram" in error_message:
                specific_error = "📸 **Instagram Restriction**\nInstagram videos may require login"
                suggestion = "Try a public Instagram post or reel"
            elif "facebook" in error_message:
                specific_error = "📘 **Facebook Restriction**\nFacebook video may be private or restricted"
                suggestion = "Try a public Facebook video"
            elif "tiktok" in error_message:
                specific_error = "🎵 **TikTok Restriction**\nTikTok video may be private or age-restricted"
                suggestion = "Try a public TikTok video"
            else:
                specific_error = f"🚫 **Download Error**\n{str(e)[:100]}{'...' if len(str(e)) > 100 else ''}"
                suggestion = "Try a different video URL"
            
            await processing_message.edit_text(
                f"❌ **Download Failed!**\n\n"
                f"{specific_error}\n\n"
                f"💡 **Suggestion:** {suggestion}\n\n"
                f"✅ **What works best:**\n"
                f"• 🎥 YouTube videos (most reliable)\n"
                f"• 📹 Public videos from supported platforms\n"
                f"• 🔓 Non-private, non-restricted content\n\n"
                f"🔄 **Try again** with a different video or contact /contact for help!",
                parse_mode='Markdown'
            )
        
        finally:
            # Clean up temporary files
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass  # Ignore cleanup errors

    async def post_init(self, application: Application):
        """Called after the bot is initialized"""
        logger.info("AnyLink Downloader Bot initialized successfully!")
        
        # Test bot connection
        try:
            bot_info = await application.bot.get_me()
            logger.info(f"Bot @{bot_info.username} is ready and listening for video URLs!")
            print(f"✅ Bot @{bot_info.username} is online and ready!")
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")

    def run(self):
        """Start the bot"""
        print("🚀 Starting AnyLink Downloader Bot...")
        print(f"👨‍💻 Developer: {self.developer_info['name']}")
        print(f"🏢 Company: {self.company_info['name']}")
        print("📱 Bot is running... Send video URLs to download!")
        print("🛑 Press Ctrl+C to stop the bot.")
        print("-" * 50)
        
        # Add post init callback
        self.application.post_init = self.post_init
        
        # Handle graceful shutdown
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal, stopping bot gracefully...")
            print("\n🛑 Shutting down bot...")
            try:
                self.application.stop()
            except:
                pass
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the bot
        try:
            self.application.run_polling(
                drop_pending_updates=True,  # Ignore old messages when starting
                allowed_updates=Update.ALL_TYPES
            )
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            print("👋 Bot stopped gracefully!")
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            print(f"❌ Bot error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import yt_dlp
        import telegram
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("📦 Please install required packages:")
        print("pip install python-telegram-bot yt-dlp")
        sys.exit(1)
    
    # Check if bot token is provided
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Bot token not configured!")
        print("🔑 Please set your bot token in the BOT_TOKEN environment variable")
        print("💡 Or replace the default token in the code")
        sys.exit(1)
    
    print("🎬 AnyLink Downloader Bot v2.0")
    print("=" * 50)
    
    bot = AnyLinkDownloaderBot()
    bot.run()
