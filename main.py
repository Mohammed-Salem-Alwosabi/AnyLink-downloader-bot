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
• YouTube
• Facebook
• Instagram
• Twitter
• TikTok
• And many more!

**How to Download:**
1. Copy the video URL from any supported platform
2. Send the URL to this bot
3. The bot will automatically download the video in the best quality available
4. Wait for the download to complete

**Features:**
📹 **Automatic Quality Selection:** The bot chooses the best available quality
🎵 **Video Format:** Downloads in MP4 format
⚡ **Fast Processing:** Quick downloads and uploads

**Commands:**
/start - Start the bot
/help - Show this help
/about - About information
/contact - Contact developer

**Tips:**
• Private videos may not be downloadable
• Very long videos might take time to process
• The bot automatically selects the best quality for you

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

**Version:** 1.0.0
**Developer:** {self.developer_info['name']}
**Company:** {self.company_info['name']}

**Description:**
AnyLink Downloader is a versatile Telegram bot designed to simplify media downloads from various online platforms. Whether it's a video from YouTube or any other supported platform, this bot provides a fast and reliable downloading experience.

**Key Features:**
• Download videos from supported URLs
• Automatic quality selection for best experience
• Support for MP4 video format
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
                "🤔 Please send me a valid video URL from supported platforms like YouTube, Facebook, Instagram, TikTok, etc.\n\n"
                "Use /help to see the full list of supported platforms!"
            )

    async def download_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """Download video directly"""
        user_id = update.effective_user.id
        
        logger.info(f"User {user_id} downloading: {url}")
        
        # Show processing message
        processing_message = await update.message.reply_text(
            f"⏳ Processing your request...\n"
            f"🔗 URL: `{url[:50]}{'...' if len(url) > 50 else ''}`\n\n"
            f"Please wait while I download the video...",
            parse_mode='Markdown'
        )
        
        temp_dir = None
        try:
            # Create temporary directory for this download
            temp_dir = tempfile.mkdtemp()
            
            # Configure yt-dlp options for best quality video
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'ignoreerrors': False,
                'no_warnings': True,
                'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best[height<=720]/best',
                'merge_output_format': 'mp4',
            }
            
            # Update status
            await processing_message.edit_text(
                f"📥 Downloading video...\n"
                f"🔗 URL: `{url[:50]}{'...' if len(url) > 50 else ''}`\n\n"
                f"⏳ This may take a few moments...",
                parse_mode='Markdown'
            )
            
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
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
                    f"The video is too large to send via Telegram. Please try with a shorter video or contact the developer for alternative solutions.",
                    parse_mode='Markdown'
                )
                return
            
            # Update status
            await processing_message.edit_text(
                f"📤 Uploading to Telegram...\n"
                f"📁 File: {title[:30]}...\n"
                f"📊 Size: {file_size / (1024*1024):.1f} MB\n\n"
                f"⏳ Almost done...",
                parse_mode='Markdown'
            )
            
            # Prepare caption
            duration_text = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
            caption = f"✅ **Download Complete!**\n\n" \
                     f"📁 **Title:** {title[:50]}{'...' if len(title) > 50 else ''}\n" \
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
                
            logger.info(f"Successfully processed download for user {user_id}")
                
        except Exception as e:
            logger.error(f"Download error for user {user_id}: {str(e)}")
            error_message = str(e)
            
            await processing_message.edit_text(
                f"❌ **Download Failed!**\n\n"
                f"🚫 Error: {error_message[:100]}{'...' if len(error_message) > 100 else ''}\n\n"
                f"💡 **Possible reasons:**\n"
                f"• Video is private or restricted\n"
                f"• URL is not supported\n"
                f"• Network connection issues\n"
                f"• Video is too long or large\n"
                f"• Geographic restrictions\n\n"
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
