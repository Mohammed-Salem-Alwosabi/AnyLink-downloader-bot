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


BOT_TOKEN = "7838776856:AAErH9mZQX1j29803t98hE9YFcab8fUm-gk"

class AnyLinkDownloaderBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.user_data = {}  # Store user preferences and states
        
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
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        
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

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "User"
        
        logger.info(f"User {user_id} ({user_name}) started the bot")
        
        # Initialize user data
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'quality': '720p',
                'format': 'Video',
                'state': 'idle'
            }
        
        welcome_message = f"""
🎬 **Welcome to AnyLink Downloader Bot, {user_name}!** 🎬

I can help you download videos and audio from various platforms including YouTube, Facebook, Instagram, and many more!

**How to use:**
1. Send me any video URL
2. Choose your preferred quality and format
3. Download and enjoy!

**Commands:**
/help - Show help information
/settings - Change download preferences
/about - About this bot
/contact - Contact developer

**Current Settings:**
📹 Format: {self.user_data[user_id]['format']}
🎯 Quality: {self.user_data[user_id]['quality']}

Just send me a video URL to get started! 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("📋 Help", callback_data="help"),
             InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("ℹ️ About", callback_data="about"),
             InlineKeyboardButton("📞 Contact", callback_data="contact")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🆘 **AnyLink Downloader Bot Help** 🆘

**Supported Platforms:**
• YouTube
• Facebook
• Instagram
• Twitter
• TikTok
• And many more!

**How to Download:**
1. Copy the video URL from any supported platform
2. Send the URL to this bot
3. Choose your preferred format (Video/Audio)
4. Select quality (360p/720p/1080p)
5. Wait for the download to complete

**Available Formats:**
📹 **Video:** MP4 format
🎵 **Audio:** MP3 format

**Quality Options:**
• 360p - Small file size
• 720p - Good quality (recommended)
• 1080p - High quality

**Commands:**
/start - Start the bot
/help - Show this help
/settings - Change preferences
/about - About information
/contact - Contact developer

**Tips:**
• Use /settings to change default quality and format
• Private videos may not be downloadable
• Very long videos might take time to process

Need more help? Use /contact to reach the developer! 👨‍💻
        """
        
        keyboard = [
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
             InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_data:
            self.user_data[user_id] = {'quality': '720p', 'format': 'Video', 'state': 'idle'}
        
        current_format = self.user_data[user_id]['format']
        current_quality = self.user_data[user_id]['quality']
        
        settings_text = f"""
⚙️ **Download Settings** ⚙️

**Current Settings:**
📹 Format: {current_format}
🎯 Quality: {current_quality}

Choose what you'd like to change:
        """
        
        keyboard = [
            [InlineKeyboardButton("📹 Change Format", callback_data="change_format"),
             InlineKeyboardButton("🎯 Change Quality", callback_data="change_quality")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = update.message if update.message else update.callback_query.message
        if update.callback_query:
            await update.callback_query.edit_message_text(settings_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await message.reply_text(settings_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /about command"""
        about_text = f"""
ℹ️ **About AnyLink Downloader Bot** ℹ️

**Version:** 1.0.0
**Developer:** {self.developer_info['name']}
**Company:** {self.company_info['name']}

**Description:**
AnyLink Downloader is a versatile Telegram bot designed to simplify media downloads from various online platforms. Whether it's a video from YouTube or audio from a music sharing site, this bot provides a fast and reliable downloading experience.

**Key Features:**
• Download videos and audio from supported URLs
• Multiple quality options (360p, 720p, 1080p)
• Support for both video (MP4) and audio (MP3) formats
• User-friendly interface with inline keyboards
• Fast and reliable downloads

**Developed with ❤️ by KaRZMa Code**

For support and updates, use /contact to reach us!
        """
        
        keyboard = [
            [InlineKeyboardButton("📞 Contact Developer", callback_data="contact"),
             InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = update.message if update.message else update.callback_query.message
        if update.callback_query:
            await update.callback_query.edit_message_text(about_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await message.reply_text(about_text, reply_markup=reply_markup, parse_mode='Markdown')

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
        
        message = update.message if update.message else update.callback_query.message
        if update.callback_query:
            await update.callback_query.edit_message_text(contact_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await message.reply_text(contact_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        data = query.data
        
        # Initialize user data if not exists
        if user_id not in self.user_data:
            self.user_data[user_id] = {'quality': '720p', 'format': 'Video', 'state': 'idle'}
        
        if data == "start":
            await self.start_command(update, context)
        elif data == "help":
            await self.help_command(update, context)
        elif data == "about":
            await self.about_command(update, context)
        elif data == "contact":
            await self.contact_command(update, context)
        elif data == "settings":
            await self.settings_command(update, context)
        elif data == "change_format":
            await self.show_format_options(update, context)
        elif data == "change_quality":
            await self.show_quality_options(update, context)
        elif data.startswith("format_"):
            format_choice = data.split("_")[1]
            self.user_data[user_id]['format'] = format_choice
            await query.edit_message_text(f"✅ Format changed to: {format_choice}")
            await asyncio.sleep(1)
            await self.settings_command(update, context)
        elif data.startswith("quality_"):
            quality_choice = data.split("_")[1]
            self.user_data[user_id]['quality'] = quality_choice
            await query.edit_message_text(f"✅ Quality changed to: {quality_choice}")
            await asyncio.sleep(1)
            await self.settings_command(update, context)
        elif data.startswith("download_"):
            parts = data.split("_", 2)
            download_format = parts[1]
            quality = parts[2] if len(parts) > 2 else "720p"
            await self.process_download(update, context, download_format, quality)

    async def show_format_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show format selection options"""
        text = "📹 **Choose Download Format:**"
        
        keyboard = [
            [InlineKeyboardButton("📹 Video (MP4)", callback_data="format_Video")],
            [InlineKeyboardButton("🎵 Audio (MP3)", callback_data="format_Audio")],
            [InlineKeyboardButton("⬅️ Back to Settings", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_quality_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show quality selection options"""
        text = "🎯 **Choose Video Quality:**"
        
        keyboard = [
            [InlineKeyboardButton("📱 360p (Small)", callback_data="quality_360p")],
            [InlineKeyboardButton("💻 720p (Recommended)", callback_data="quality_720p")],
            [InlineKeyboardButton("🖥️ 1080p (High Quality)", callback_data="quality_1080p")],
            [InlineKeyboardButton("⬅️ Back to Settings", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (URLs)"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        logger.info(f"User {user_id} sent message: {message_text[:50]}...")
        
        # Initialize user data if not exists
        if user_id not in self.user_data:
            self.user_data[user_id] = {'quality': '720p', 'format': 'Video', 'state': 'idle'}
        
        # Check if message contains a URL
        if any(protocol in message_text.lower() for protocol in ['http://', 'https://', 'www.']):
            await self.handle_url(update, context, message_text)
        else:
            await update.message.reply_text(
                "🤔 Please send me a valid video URL from supported platforms like YouTube, Facebook, Instagram, etc.\n\n"
                "Use /help to see the full list of supported platforms!"
            )

    async def handle_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """Handle URL and show download options"""
        user_id = update.effective_user.id
        
        # Store the URL for this user
        self.user_data[user_id]['current_url'] = url
        
        # Show download options
        text = f"""
🔗 **URL Received:** 
`{url[:50]}{'...' if len(url) > 50 else ''}`

📋 **Choose download option:**
        """
        
        keyboard = [
            [InlineKeyboardButton("📹 Video 720p", callback_data="download_Video_720p"),
             InlineKeyboardButton("📹 Video 1080p", callback_data="download_Video_1080p")],
            [InlineKeyboardButton("📹 Video 360p", callback_data="download_Video_360p"),
             InlineKeyboardButton("🎵 Audio MP3", callback_data="download_Audio_192")],
            [InlineKeyboardButton("⚙️ Custom Settings", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def process_download(self, update: Update, context: ContextTypes.DEFAULT_TYPE, download_format: str, quality: str):
        """Process the download request"""
        user_id = update.effective_user.id
        
        if 'current_url' not in self.user_data[user_id]:
            await update.callback_query.edit_message_text("❌ No URL found. Please send a video URL first.")
            return
        
        url = self.user_data[user_id]['current_url']
        logger.info(f"User {user_id} downloading: {url} - Format: {download_format}, Quality: {quality}")
        
        # Show processing message
        processing_message = await update.callback_query.edit_message_text(
            f"⏳ Processing your request...\n"
            f"📹 Format: {download_format}\n"
            f"🎯 Quality: {quality}\n"
            f"🔗 URL: `{url[:50]}{'...' if len(url) > 50 else ''}`",
            parse_mode='Markdown'
        )
        
        temp_dir = None
        try:
            # Create temporary directory for this download
            temp_dir = tempfile.mkdtemp()
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'ignoreerrors': False,
                'no_warnings': True,
            }
            
            if download_format == "Video":
                if quality == "360p":
                    ydl_opts['format'] = 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                elif quality == "720p":
                    ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                elif quality == "1080p":
                    ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
            
            elif download_format == "Audio":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            # Update status
            await processing_message.edit_text(
                f"📥 Downloading...\n"
                f"📹 Format: {download_format}\n"
                f"🎯 Quality: {quality}",
                parse_mode='Markdown'
            )
            
            # Download the video/audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown')
                
            # Find the downloaded file
            downloaded_files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            
            if not downloaded_files:
                raise Exception("No file was downloaded")
            
            file_path = os.path.join(temp_dir, downloaded_files[0])
            file_size = os.path.getsize(file_path)
            
            # Check file size (Telegram limit is 50MB for bots)
            if file_size > 50 * 1024 * 1024:  # 50MB
                await processing_message.edit_text(
                    f"❌ **File too large!**\n\n"
                    f"📁 File size: {file_size / (1024*1024):.1f} MB\n"
                    f"⚠️ Telegram limit: 50 MB\n\n"
                    f"Try downloading with lower quality or contact the developer for alternative solutions.",
                    parse_mode='Markdown'
                )
                return
            
            # Update status
            await processing_message.edit_text(
                f"📤 Uploading to Telegram...\n"
                f"📁 File: {title[:30]}...\n"
                f"📊 Size: {file_size / (1024*1024):.1f} MB",
                parse_mode='Markdown'
            )
            
            # Send the file
            caption = f"✅ **Download Complete!**\n\n" \
                     f"📁 **Title:** {title[:50]}{'...' if len(title) > 50 else ''}\n" \
                     f"📹 **Format:** {download_format}\n" \
                     f"🎯 **Quality:** {quality}\n" \
                     f"📊 **Size:** {file_size / (1024*1024):.1f} MB\n\n" \
                     f"🤖 **Downloaded by AnyLink Downloader Bot**"
            
            with open(file_path, 'rb') as file:
                if download_format == "Video":
                    await context.bot.send_video(
                        chat_id=update.effective_chat.id,
                        video=file,
                        caption=caption,
                        parse_mode='Markdown'
                    )
                else:
                    await context.bot.send_audio(
                        chat_id=update.effective_chat.id,
                        audio=file,
                        caption=caption,
                        parse_mode='Markdown'
                    )
            
            # Delete the processing message
            await processing_message.delete()
            
            # Clear the current URL
            if 'current_url' in self.user_data[user_id]:
                del self.user_data[user_id]['current_url']
                
            logger.info(f"Successfully processed download for user {user_id}")
                
        except Exception as e:
            logger.error(f"Download error for user {user_id}: {str(e)}")
            await processing_message.edit_text(
                f"❌ **Download Failed!**\n\n"
                f"🚫 Error: {str(e)[:100]}{'...' if len(str(e)) > 100 else ''}\n\n"
                f"💡 **Possible reasons:**\n"
                f"• Video is private or restricted\n"
                f"• URL is not supported\n"
                f"• Network connection issues\n"
                f"• Video is too long or large\n\n"
                f"Try with a different URL or contact support!",
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
        print("🚀 Starting AnyLink Downloader Bot...")
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
    # Check if required packages are installed - I will delete this later hhhh 
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
    
    
    