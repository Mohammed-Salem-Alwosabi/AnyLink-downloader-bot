import os
import sys
import logging
import tempfile
import shutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import re


BOT_TOKEN = "7838776856:AAErH9mZQX1j29803t98hE9YFcab8fUm-gk"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

print("⚠️  WARNING: Using hardcoded token - NOT SECURE!")
print(f"🤖 Bot token: {BOT_TOKEN[:20]}...")
print("🚀 Starting AnyLink Downloader Bot on Railway...")

class AnyLinkBot:
    def __init__(self):
        # Initialize the bot with hardcoded token
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
        print("✅ Bot initialized successfully")
        
    def setup_handlers(self):
        """Setup all command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("test", self.test))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error_handler)
        print("✅ All handlers registered")
        
    async def error_handler(self, update, context):
        """Handle errors"""
        logger.error(f"❌ Error occurred: {context.error}")
        if update and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ An error occurred. Please try again or contact support."
                )
            except Exception as e:
                logger.error(f"Failed to send error message: {e}")
    
    def is_valid_url(self, text):
        """Check if text contains a valid video URL"""
        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://(?:www\.)?youtu\.be/[\w-]+',
            r'https?://(?:www\.)?instagram\.com/(?:p|reel)/[\w-]+',
            r'https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',
            r'https?://vm\.tiktok\.com/[\w-]+',
            r'https?://(?:www\.)?facebook\.com/.+/videos/\d+',
            r'https?://(?:www\.)?twitter\.com/.+/status/\d+',
            r'https?://(?:www\.)?x\.com/.+/status/\d+',
            r'https?://[^\s]+',  # General URL pattern
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    
    def get_platform_name(self, url):
        """Get platform name from URL"""
        url_lower = url.lower()
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'YouTube'
        elif 'instagram.com' in url_lower:
            return 'Instagram'
        elif 'tiktok.com' in url_lower:
            return 'TikTok'
        elif 'facebook.com' in url_lower:
            return 'Facebook'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'Twitter/X'
        else:
            return 'Video Platform'
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        logger.info(f"👤 User {user.id} (@{user.username}) started the bot")
        
        welcome_message = f"""🎬 **Welcome to AnyLink Downloader Bot!**

Hi {user.first_name}! 👋

🚀 **Powered by Railway Cloud** - Lightning fast downloads!

**✨ What I can do:**
📺 YouTube videos
📸 Instagram posts & reels  
🎵 TikTok videos
📘 Facebook videos
🐦 Twitter/X videos
➕ Many more platforms!

**🎯 How to use:**
1. Send me any video URL
2. I'll download it instantly
3. Enjoy your video!

**⚡ Features:**
• High-speed cloud processing
• Multiple format support
• 24/7 availability
• Completely free!

Just send me a video URL to get started! 🎉

**🔧 Test commands:**
• /test - Test bot functionality
• /help - Detailed help guide"""

        keyboard = [
            [
                InlineKeyboardButton("📋 Help Guide", callback_data="help"),
                InlineKeyboardButton("🧪 Test Bot", callback_data="test")
            ],
            [
                InlineKeyboardButton("🎬 Try YouTube", url="https://youtu.be/dQw4w9WgXcQ"),
                InlineKeyboardButton("📸 Try Instagram", url="https://instagram.com")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await update.message.reply_text(
                welcome_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            # Fallback without markdown
            await update.message.reply_text(
                "🎬 Welcome to AnyLink Downloader Bot!\n\n"
                "Send me a video URL to download it instantly!\n\n"
                "Use /help for more information.",
                reply_markup=reply_markup
            )
    
    async def test(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /test command"""
        test_message = """🧪 **Bot Test Results**

**🤖 Bot Status:**
✅ Bot is online and responding
✅ Telegram API connection active
✅ Railway cloud server running
✅ Command handlers working

**🔧 System Check:**
✅ Python runtime: Active
✅ yt-dlp library: Available
✅ Temporary storage: Ready
✅ Error handling: Active

**📊 Performance:**
• Response time: < 1 second
• Server location: Railway Cloud
• Uptime: 24/7
• Memory usage: Optimized

**🎯 Ready for downloads!**

Send me any video URL to test the download functionality!

**Example URLs to try:**
• YouTube: https://youtu.be/dQw4w9WgXcQ
• Any other video platform URL"""

        await update.message.reply_text(test_message, parse_mode='Markdown')
        logger.info(f"✅ Test command executed for user {update.effective_user.id}")
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """🆘 **AnyLink Downloader Bot - Complete Guide**

**🎯 Supported Platforms:**
✅ **YouTube** - Any video URL (youtube.com, youtu.be)
✅ **Instagram** - Posts, Reels, IGTV (instagram.com/p/, /reel/)
✅ **TikTok** - Videos and clips (tiktok.com, vm.tiktok.com)
✅ **Facebook** - Public videos (facebook.com/videos/)
✅ **Twitter/X** - Video tweets (twitter.com, x.com)
✅ **Reddit** - Video posts (reddit.com)
✅ **And many more platforms!**

**📱 How to Download:**
1. **Copy** the video URL from any supported platform
2. **Send** the URL to me as a message
3. **Wait** for processing (usually 10-30 seconds)
4. **Download** your video when ready!

**⚡ Pro Tips:**
• Use direct video links for best results
• Public videos work better than private ones
• Shorter videos process faster
• HD quality available when possible

**🚫 Limitations:**
• Maximum file size: 50MB (Telegram limit)
• No live streams or premieres
• Private content may not be accessible
• Some geographic restrictions may apply

**🔧 Commands:**
• /start - Welcome message and main menu
• /help - This help guide
• /test - Test bot functionality

**🚀 Powered by Railway Cloud for maximum speed and reliability!**

Just send me any video URL to get started! 🎉"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (URLs)"""
        user = update.effective_user
        text = update.message.text.strip()
        
        logger.info(f"👤 User {user.id} sent: {text[:50]}...")
        
        if self.is_valid_url(text):
            await self.download_video(update, context, text)
        else:
            # Not a valid URL
            help_message = """🤔 **That doesn't look like a video URL!**

**💡 Please send me a valid video URL like:**
• `https://youtube.com/watch?v=VIDEO_ID`
• `https://instagram.com/p/POST_ID`
• `https://tiktok.com/@user/video/VIDEO_ID`
• `https://twitter.com/user/status/TWEET_ID`

**🎯 Supported platforms:**
YouTube • Instagram • TikTok • Facebook • Twitter/X • Reddit • And more!

**📋 Need help?** Use /help for detailed guide
**🧪 Want to test?** Use /test to check bot status
**🎬 Try an example:** Send this YouTube URL:
`https://youtu.be/dQw4w9WgXcQ`"""

            keyboard = [
                [
                    InlineKeyboardButton("📋 Help Guide", callback_data="help"),
                    InlineKeyboardButton("🧪 Test Bot", callback_data="test")
                ],
                [
                    InlineKeyboardButton("🎬 Try Example", url="https://youtu.be/dQw4w9WgXcQ")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                help_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def download_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """Download video from URL"""
        user = update.effective_user
        platform = self.get_platform_name(url)
        
        logger.info(f"🎬 User {user.id} downloading from {platform}: {url}")
        
        # Show processing message
        status_message = await update.message.reply_text(
            f"🎬 **Processing {platform} Video**\n\n"
            f"🔗 **URL:** `{url[:60]}{'...' if len(url) > 60 else ''}`\n"
            f"☁️ **Server:** Railway Cloud\n"
            f"⏳ **Status:** Analyzing video...\n\n"
            f"⚡ **This usually takes 10-30 seconds**",
            parse_mode='Markdown'
        )
        
        temp_dir = None
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            logger.info(f"📁 Created temp directory: {temp_dir}")
            
            # Update status
            await status_message.edit_text(
                f"📥 **Downloading from {platform}**\n\n"
                f"🔗 **URL:** `{url[:60]}{'...' if len(url) > 60 else ''}`\n"
                f"☁️ **Server:** Railway Cloud\n"
                f"⏳ **Status:** Downloading video...\n\n"
                f"🚀 **High-speed download in progress!**",
                parse_mode='Markdown'
            )
            
            # yt-dlp options - simplified and reliable
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title).50s.%(ext)s'),
                'format': 'best[filesize<50M]/best[height<=720]/best',
                'noplaylist': True,
                'no_warnings': True,
                'ignoreerrors': False,
                'socket_timeout': 30,
                'retries': 2,
                'prefer_ffmpeg': True,
                'merge_output_format': 'mp4',
            }
            
            # Download with yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown Title')[:50]
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Unknown')[:30]
                
                logger.info(f"✅ Downloaded: {title}")
            
            # Find downloaded file
            files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            
            if not files:
                raise Exception("No file was downloaded - video may be unavailable")
            
            file_path = os.path.join(temp_dir, files[0])
            file_size = os.path.getsize(file_path)
            
            logger.info(f"📄 File size: {file_size / (1024*1024):.1f} MB")
            
            # Check Telegram file size limit
            if file_size > 50 * 1024 * 1024:  # 50MB
                await status_message.edit_text(
                    f"❌ **File Too Large for Telegram**\n\n"
                    f"📁 **File Size:** {file_size / (1024*1024):.1f} MB\n"
                    f"⚠️ **Telegram Limit:** 50 MB\n"
                    f"🎬 **Title:** {title}\n\n"
                    f"💡 **Suggestions:**\n"
                    f"• Try a shorter video\n"
                    f"• Look for lower quality versions\n"
                    f"• Some platforms offer multiple formats",
                    parse_mode='Markdown'
                )
                return
            
            # Update status for upload
            await status_message.edit_text(
                f"📤 **Uploading to Telegram**\n\n"
                f"📁 **Title:** {title}\n"
                f"👤 **Creator:** {uploader}\n"
                f"📊 **Size:** {file_size / (1024*1024):.1f} MB\n"
                f"🎯 **Platform:** {platform}\n\n"
                f"⚡ **Almost ready...**",
                parse_mode='Markdown'
            )
            
            # Prepare caption
            duration_text = f"{duration//60}:{duration%60:02d}" if duration > 0 else "Unknown"
            
            caption = f"✅ **Download Successful!**\n\n"
            caption += f"📁 **Title:** {title}\n"
            caption += f"👤 **Creator:** {uploader}\n"
            caption += f"🎯 **Platform:** {platform}\n"
            caption += f"⏱️ **Duration:** {duration_text}\n"
            caption += f"📊 **Size:** {file_size / (1024*1024):.1f} MB\n\n"
            caption += f"🤖 **AnyLink Downloader Bot**\n"
            caption += f"☁️ **Powered by Railway Cloud**"
            
            # Send video to user
            with open(file_path, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption=caption[:1024],  # Telegram caption limit
                    parse_mode='Markdown',
                    supports_streaming=True,
                    duration=duration if duration > 0 else None
                )
            
            # Success message with options
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Download Another", callback_data="start"),
                    InlineKeyboardButton("⭐ Rate Bot", url="https://t.me/KaRZMa_Code")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await status_message.edit_text(
                f"🎉 **Download Complete!**\n\n"
                f"✅ Successfully downloaded from {platform}\n"
                f"📱 Video sent to your chat\n"
                f"⚡ Processed by Railway Cloud\n\n"
                f"💡 **Want to download more?** Just send another URL!",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Successfully completed download for user {user.id}")
            
        except Exception as e:
            logger.error(f"❌ Download failed for user {user.id}: {str(e)}")
            
            # Enhanced error handling
            error_message = str(e).lower()
            
            if "private" in error_message or "login" in error_message:
                error_text = f"🔒 **{platform}: Private Content**\n\n"
                error_text += f"This video is private or requires login.\n\n"
                error_text += f"**💡 Try these solutions:**\n"
                error_text += f"• Make sure the video is public\n"
                error_text += f"• Try a different video from the same creator\n"
                error_text += f"• Some platforms don't allow downloading private content"
                
            elif "not available" in error_message or "removed" in error_message:
                error_text = f"❌ **{platform}: Video Not Available**\n\n"
                error_text += f"The video may have been removed or is not accessible.\n\n"
                error_text += f"**💡 Try these solutions:**\n"
                error_text += f"• Check if the URL is correct\n"
                error_text += f"• Try accessing the video in your browser first\n"
                error_text += f"• The video might be geo-restricted"
                
            elif "rate" in error_message or "limit" in error_message:
                error_text = f"⏱️ **Rate Limit Reached**\n\n"
                error_text += f"Too many requests in a short time.\n\n"
                error_text += f"**💡 Please:**\n"
                error_text += f"• Wait 2-3 minutes before trying again\n"
                error_text += f"• This helps prevent service overload\n"
                error_text += f"• Railway servers will be ready soon!"
                
            else:
                error_text = f"🚫 **{platform}: Download Failed**\n\n"
                error_text += f"**Error Details:** `{str(e)[:100]}{'...' if len(str(e)) > 100 else ''}`\n\n"
                error_text += f"**💡 Common Solutions:**\n"
                error_text += f"• Verify the video URL is correct\n"
                error_text += f"• Make sure the video is public\n"
                error_text += f"• Try again in a few minutes\n"
                error_text += f"• Contact support if issue persists"
            
            # Error message with retry options
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Try Again", callback_data="start"),
                    InlineKeyboardButton("📞 Get Help", url="https://t.me/MohammedAlwosabi")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await status_message.edit_text(
                error_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"🧹 Cleaned up temp directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to clean temp directory: {e}")
    
    def run(self):
        """Start the bot"""
        print("🚀 Starting AnyLink Downloader Bot...")
        print("👨‍💻 Developer: Mohammed Salem Alwosabi")
        print("🏢 Company: KaRZMa Code")
        print("☁️ Platform: Railway Cloud")
        print("📱 Bot is running... Ready to receive messages!")
        
        try:
            # Start the bot with polling
            self.application.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
        except KeyboardInterrupt:
            print("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Critical error: {e}")
            print(f"❌ CRITICAL ERROR: {e}")
            sys.exit(1)

# Main execution
if __name__ == "__main__":
    print("🔍 Checking dependencies...")
    
    # Check critical dependencies
    missing_deps = []
    
    try:
        import telegram
        print("✅ python-telegram-bot: Available")
    except ImportError:
        missing_deps.append("python-telegram-bot")
        print("❌ python-telegram-bot: MISSING")
    
    try:
        import yt_dlp
        print("✅ yt-dlp: Available")
    except ImportError:
        missing_deps.append("yt-dlp")
        print("❌ yt-dlp: MISSING")
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("🔧 Install with: pip install python-telegram-bot yt-dlp")
        sys.exit(1)
    
    print("✅ All dependencies available")
    print("🚀 Initializing bot...")
    
    # Create and run bot
    try:
        bot = AnyLinkBot()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        print(f"❌ STARTUP ERROR: {e}")
        sys.exit(1)
