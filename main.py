#AnyLink Downloader Bot - Fixed Version
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

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

class AnyLinkDownloaderBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Developer and company info
        self.developer_info = {
            'name': 'Mohammed Salem Alwosabi',
            'email': 'm.salem.alwosabi@gmail.com',
            'whatsapp': '+967739003665',
            'telegram': '@MohammedAlwosabi'
        }
        
        self.company_info = {
            'name': 'KaRZMa Code',
            'telegram': 'https://t.me/KaRZMa_Code'
        }
        
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
        """Handle errors"""
        logger.error("Exception while handling an update:", exc_info=context.error)
        
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
        
        welcome_message = f"""
🎬 **Welcome to AnyLink Downloader Bot, {user_name}!** 🎬

I can help you download videos from various platforms including YouTube, Facebook, Instagram, TikTok, and many more!

**How to use:**
1. 📋 Copy any video URL from supported platforms
2. 📤 Send the URL to me in this chat
3. ⏳ I'll process and download the video
4. 📱 You'll receive the video file directly in this chat

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

**Limitations:**
🔒 Private videos cannot be downloaded
📏 Maximum file size: 50MB (Telegram limit)
🌍 Some geo-restricted content may not work

Need help? Use /contact to reach the developer! 👨‍💻
        """
        
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="start")]]
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

**Version:** 2.1.0 (Fixed)
**Developer:** {self.developer_info['name']}
**Company:** {self.company_info['name']}

**Description:**
AnyLink Downloader is a versatile Telegram bot designed to simplify media downloads from various online platforms.

**Developed with ❤️ by KaRZMa Code**
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
        message_text = update.message.text.strip()
        
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
                "💡 Use /help to see the complete list of supported platforms.",
                parse_mode='Markdown'
            )

    async def download_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """Download video and send it back to user"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "User"
        
        logger.info(f"User {user_id} ({user_name}) downloading: {url}")
        
        processing_message = await update.message.reply_text(
            f"🎬 **Processing Video Download**\n\n"
            f"👤 **User:** {user_name}\n"
            f"🔗 **URL:** `{url[:60]}{'...' if len(url) > 60 else ''}`\n\n"
            f"⏳ **Status:** Analyzing video...",
            parse_mode='Markdown'
        )
        
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp()
            
            # FIXED: Updated yt-dlp configuration with better options
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'format': 'best[filesize<50M][ext=mp4]/best[filesize<50M]/worst[ext=mp4]/worst',
                'noplaylist': True,
                'no_warnings': True,
                'ignoreerrors': False,
                'extract_flat': False,
                'writethumbnail': False,
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                # FIXED: Updated headers and user agent
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip,deflate',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                    'Connection': 'keep-alive'
                },
                # FIXED: Added these important options
                'sleep_interval': 1,
                'max_sleep_interval': 5,
                'fragment_retries': 10,
                'retries': 3,
                'socket_timeout': 30,
                # FIXED: Better geo handling
                'geo_bypass': True,
                'geo_bypass_country': 'US',
                # FIXED: No cookies initially (add if needed)
                'cookiefile': None,
            }
            
            success = False
            title = "Unknown Video"
            duration = 0
            file_size = 0
            
            # FIXED: Simplified download approach
            try:
                await processing_message.edit_text(
                    f"🎬 **Processing Video Download**\n\n"
                    f"👤 **User:** {user_name}\n"
                    f"🔗 **URL:** `{url[:60]}{'...' if len(url) > 60 else ''}`\n\n"
                    f"📥 **Status:** Downloading video...\n"
                    f"⏳ This may take a few moments...",
                    parse_mode='Markdown'
                )
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # FIXED: Extract info first, then download
                    info = ydl.extract_info(url, download=False)
                    
                    # Check if video is too large before downloading
                    if 'filesize' in info and info['filesize']:
                        if info['filesize'] > 50 * 1024 * 1024:  # 50MB
                            await processing_message.edit_text(
                                f"❌ **File Too Large for Telegram!**\n\n"
                                f"📁 **Video Title:** {info.get('title', 'Unknown')[:50]}...\n"
                                f"📊 **File Size:** {info['filesize'] / (1024*1024):.1f} MB\n"
                                f"⚠️ **Telegram Limit:** 50 MB maximum\n\n"
                                f"💡 Try a shorter video or different quality.",
                                parse_mode='Markdown'
                            )
                            return
                    
                    # Now download
                    ydl.download([url])
                    
                    title = info.get('title', 'Unknown Video')
                    duration = info.get('duration', 0)
                    
                success = True
                logger.info(f"Successfully downloaded video")
                    
            except yt_dlp.DownloadError as e:
                error_msg = str(e).lower()
                if "private" in error_msg or "login" in error_msg:
                    raise Exception("This video is private or requires login")
                elif "geo" in error_msg or "country" in error_msg:
                    raise Exception("Video is geo-blocked in this region")
                elif "copyright" in error_msg:
                    raise Exception("Video removed due to copyright")
                elif "not available" in error_msg:
                    raise Exception("Video not available or has been removed")
                else:
                    raise Exception(f"Download failed: {str(e)}")
            except Exception as e:
                raise Exception(f"Unexpected error: {str(e)}")
            
            if not success:
                raise Exception("Download failed for unknown reason")
            
            # Find downloaded file
            downloaded_files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            
            if not downloaded_files:
                raise Exception("No file was downloaded")
            
            file_path = os.path.join(temp_dir, downloaded_files[0])
            file_size = os.path.getsize(file_path)
            
            # Final size check
            if file_size > 50 * 1024 * 1024:
                await processing_message.edit_text(
                    f"❌ **File Too Large!**\n\n"
                    f"📊 **Size:** {file_size / (1024*1024):.1f} MB\n"
                    f"⚠️ **Limit:** 50 MB\n\n"
                    f"💡 Try a different video.",
                    parse_mode='Markdown'
                )
                return
            
            if file_size < 1024:  # Less than 1KB
                raise Exception("Downloaded file is too small or corrupted")
            
            # Update status for upload
            await processing_message.edit_text(
                f"🎬 **Uploading Video**\n\n" 
                f"📁 **Title:** {title[:40]}{'...' if len(title) > 40 else ''}\n"
                f"📊 **Size:** {file_size / (1024*1024):.1f} MB\n\n"
                f"📤 **Status:** Uploading to Telegram...",
                parse_mode='Markdown'
            )
            
            # Prepare caption
            duration_text = f"{duration//60}:{duration%60:02d}" if duration > 0 else "Unknown"
            
            caption = f"✅ **Download Complete!**\n\n" \
                     f"📁 **Title:** {title[:100]}{'...' if len(title) > 100 else ''}\n" \
                     f"⏱️ **Duration:** {duration_text}\n" \
                     f"📊 **Size:** {file_size / (1024*1024):.1f} MB\n\n" \
                     f"💾 **To Save:** Long press → Save to Gallery\n\n" \
                     f"🤖 **@AnyLinkDownloaderBot by KaRZMa Code**"
            
            # Send video
            with open(file_path, 'rb') as file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=file,
                    caption=caption,
                    parse_mode='Markdown',
                    supports_streaming=True,
                    duration=duration if duration > 0 else None
                )
            
            # Delete processing message
            try:
                await processing_message.delete()
            except:
                pass
                
            logger.info(f"Successfully delivered video to user {user_id}")
                
        except Exception as e:
            logger.error(f"Download error for user {user_id}: {str(e)}")
            
            # Provide specific error messages
            error_message = str(e).lower()
            
            if "private" in error_message or "login" in error_message:
                specific_error = "🔒 **Private Content**\nThis video requires login or is private"
                suggestion = "Try a public video"
            elif "geo" in error_message or "country" in error_message:
                specific_error = "🌍 **Geo-Restricted**\nVideo not available in this region"
                suggestion = "Try a different video"
            elif "not available" in error_message or "removed" in error_message:
                specific_error = "❌ **Video Unavailable**\nVideo has been removed or is no longer available"
                suggestion = "Check if the video URL is still valid"
            elif "copyright" in error_message:
                specific_error = "©️ **Copyright Issue**\nVideo removed due to copyright"
                suggestion = "Try a different video"
            else:
                specific_error = f"🚫 **Download Error**\n{str(e)[:100]}..."
                suggestion = "Try a different video URL"
            
            await processing_message.edit_text(
                f"❌ **Download Failed!**\n\n"
                f"{specific_error}\n\n"
                f"💡 **Suggestion:** {suggestion}\n\n"
                f"✅ **What works best:**\n"
                f"• 🎥 YouTube videos (most reliable)\n"
                f"• 📹 Public videos only\n"
                f"• 🔓 Non-restricted content\n\n"
                f"🔄 Try again with a different video!",
                parse_mode='Markdown'
            )
        
        finally:
            # Cleanup
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass

    def run(self):
        """Start the bot"""
        print("🚀 Starting AnyLink Downloader Bot (Fixed Version)...")
        print(f"👨‍💻 Developer: {self.developer_info['name']}")
        print(f"🏢 Company: {self.company_info['name']}")
        print("📱 Bot is running... Send video URLs to download!")
        print("🛑 Press Ctrl+C to stop the bot.")
        print("-" * 50)
        
        def signal_handler(signum, frame):
            logger.info("Shutting down bot gracefully...")
            print("\n🛑 Shutting down bot...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            self.application.run_polling(
                drop_pending_updates=True,
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
    # Check packages
    try:
        import yt_dlp
        import telegram
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("📦 Install with: pip install python-telegram-bot yt-dlp")
        sys.exit(1)
    
    # Check token
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Bot token not configured!")
        print("🔑 Set BOT_TOKEN environment variable or replace in code")
        sys.exit(1)
    
    print("🎬 AnyLink Downloader Bot v2.1 (Fixed)")
    print("=" * 50)
    
    bot = AnyLinkDownloaderBot()
    bot.run()
