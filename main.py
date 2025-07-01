# main.py - Anti-Bot Detection Fixed Version
import os
import sys
import logging
import tempfile
import shutil
import random
import time
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import re

# Hardcoded token
BOT_TOKEN = "7838776856:AAErH9mZQX1j29803t98hE9YFcab8fUm-gk"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

print("🛡️ Anti-Bot Detection Version Loading...")
print(f"🤖 Bot token: {BOT_TOKEN[:20]}...")
print("🚀 Starting AnyLink Downloader Bot with Bot Detection Bypass...")

class AntiBotDownloaderBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Multiple user agents to rotate
        self.user_agents = [
            # Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            # Chrome on Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            # Chrome on Linux
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            # Safari on Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
        ]
        
        self.setup_handlers()
        
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("test", self.test_download))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error_handler)
        
    async def error_handler(self, update, context):
        logger.error(f"❌ Error: {context.error}")
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ An error occurred. Please try again."
            )
    
    def is_valid_url(self, text):
        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://(?:www\.)?youtu\.be/[\w-]+',
            r'https?://(?:www\.)?instagram\.com/(?:p|reel)/[\w-]+',
            r'https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',
            r'https?://vm\.tiktok\.com/[\w-]+',
            r'https?://[^\s]+',
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    
    def get_platform_name(self, url):
        url_lower = url.lower()
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'YouTube'
        elif 'instagram.com' in url_lower:
            return 'Instagram'
        elif 'tiktok.com' in url_lower:
            return 'TikTok'
        else:
            return 'Video Platform'
    
    def get_anti_bot_options(self, temp_dir, platform='youtube', attempt=1):
        """Get yt-dlp options with anti-bot detection"""
        
        # Random user agent
        user_agent = random.choice(self.user_agents)
        
        # Base options with anti-detection
        base_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title).50s.%(ext)s'),
            'noplaylist': True,
            'no_warnings': False,
            'ignoreerrors': False,
            'socket_timeout': 30,
            'retries': 3,
            'user_agent': user_agent,
            
            # Anti-bot detection headers
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            },
            
            # Random delays to appear human-like
            'sleep_interval': random.uniform(1, 3),
            'max_sleep_interval': 5,
        }
        
        # Platform-specific anti-bot configurations
        if platform == 'youtube':
            if attempt == 1:
                # First attempt: Standard approach with anti-detection
                base_opts.update({
                    'format': 'best[height<=720][filesize<50M]/best[filesize<50M]/best',
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web'],
                            'skip': ['dash'],
                        }
                    }
                })
            elif attempt == 2:
                # Second attempt: Mobile client simulation
                base_opts.update({
                    'format': 'best[height<=480]/worst',
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android'],
                            'skip': ['dash', 'hls'],
                        }
                    },
                    'http_headers': {
                        **base_opts['http_headers'],
                        'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 11) gzip',
                    }
                })
            elif attempt == 3:
                # Third attempt: Alternative extractor
                base_opts.update({
                    'format': 'worst/best',
                    'prefer_insecure': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web'],
                        }
                    }
                })
            else:
                # Last attempt: Most basic settings
                base_opts.update({
                    'format': 'worst',
                    'prefer_insecure': True,
                    'no_check_certificate': True,
                })
        else:
            # Non-YouTube platforms
            base_opts.update({
                'format': 'best[filesize<50M]/best',
            })
        
        return base_opts
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome = """🎬 **AnyLink Downloader Bot**
        
🛡️ **Anti-Bot Detection Enabled**
🚀 **Powered by Railway Cloud**

**✨ What I can do:**
📺 YouTube videos (bot detection bypass)
📸 Instagram posts & reels  
🎵 TikTok videos
📘 Facebook videos
🐦 Twitter/X videos

**🎯 How to use:**
1. Send me any video URL
2. I'll bypass bot detection automatically
3. Download your video!

**⚡ Anti-Bot Features:**
• Multiple user agents rotation
• Human-like request delays
• Advanced header simulation
• Mobile client emulation
• Multiple retry strategies

Send me a video URL to test! 🎉"""
        
        keyboard = [
            [
                InlineKeyboardButton("📋 Help", callback_data="help"),
                InlineKeyboardButton("🧪 Test YouTube", callback_data="test")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome, parse_mode='Markdown', reply_markup=reply_markup)
        
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """🆘 **Anti-Bot Downloader Help**

**🛡️ Bot Detection Bypass:**
This version includes advanced anti-bot detection to bypass YouTube's "Sign in to confirm you're not a bot" error.

**🎯 Supported Platforms:**
✅ **YouTube** - With bot detection bypass
✅ **Instagram** - Posts, Reels, IGTV
✅ **TikTok** - Videos and clips
✅ **Facebook** - Public videos
✅ **Twitter/X** - Video tweets

**🔧 Anti-Bot Features:**
• **User Agent Rotation** - Appears as different browsers
• **Request Delays** - Human-like timing
• **Header Simulation** - Mimics real browser requests
• **Mobile Emulation** - Uses mobile YouTube client
• **Retry Logic** - Multiple bypass attempts

**📱 How to use:**
1. Send any video URL
2. Bot automatically tries multiple bypass methods
3. Get your video!

**💡 Tips:**
• Works best with public videos
• May take 30-60 seconds for YouTube
• Multiple attempts automatically tried
• Railway cloud optimized

Just send me any video URL! 🚀"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def test_download(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test with a known YouTube URL"""
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - always works
        
        await update.message.reply_text(
            f"🧪 **Testing Anti-Bot Detection**\n\n"
            f"Testing with: `{test_url}`\n"
            f"This will test all bypass methods.\n\n"
            f"⏳ Starting anti-bot test...",
            parse_mode='Markdown'
        )
        
        await self.download_with_antibot(update, context, test_url, is_test=True)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        
        if self.is_valid_url(text):
            await self.download_with_antibot(update, context, text)
        else:
            await update.message.reply_text(
                "🤔 **Please send a valid video URL**\n\n"
                "**Examples:**\n"
                "• `https://youtube.com/watch?v=VIDEO_ID`\n"
                "• `https://instagram.com/p/POST_ID`\n"
                "• `https://tiktok.com/@user/video/VIDEO_ID`\n\n"
                "**🧪 Test:** Send `/test` for YouTube test\n"
                "**📋 Help:** Send `/help` for more info",
                parse_mode='Markdown'
            )
    
    async def download_with_antibot(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, is_test=False):
        """Download with anti-bot detection bypass"""
        user_id = update.effective_user.id
        platform = self.get_platform_name(url)
        
        logger.info(f"🛡️ User {user_id} downloading from {platform} with anti-bot: {url}")
        
        status_msg = await update.message.reply_text(
            f"🛡️ **Anti-Bot Detection Active**\n\n"
            f"🔗 **URL:** `{url[:50]}...`\n"
            f"🎯 **Platform:** {platform}\n"
            f"⏳ **Status:** Initializing bypass...\n\n"
            f"🔄 **This may take 30-60 seconds**",
            parse_mode='Markdown'
        )
        
        temp_dir = None
        max_attempts = 4 if platform == 'YouTube' else 2
        
        try:
            temp_dir = tempfile.mkdtemp()
            
            # Try multiple anti-bot methods
            for attempt in range(1, max_attempts + 1):
                try:
                    await status_msg.edit_text(
                        f"🛡️ **Anti-Bot Method {attempt}/{max_attempts}**\n\n"
                        f"🔗 **URL:** `{url[:50]}...`\n"
                        f"🎯 **Platform:** {platform}\n"
                        f"⏳ **Status:** Bypassing detection...\n\n"
                        f"🔧 **Method:** {'Mobile Client' if attempt == 2 else 'Web Client' if attempt == 1 else 'Alternative' if attempt == 3 else 'Basic'}\n"
                        f"⚡ **Please wait...**",
                        parse_mode='Markdown'
                    )
                    
                    # Add human-like delay before attempt
                    if attempt > 1:
                        delay = random.uniform(3, 7)
                        await asyncio.sleep(delay)
                    
                    # Get anti-bot options for this attempt
                    ydl_opts = self.get_anti_bot_options(temp_dir, platform.lower(), attempt)
                    
                    # Clear previous files
                    for file in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    
                    logger.info(f"🔄 Attempt {attempt} with anti-bot method")
                    
                    # Try download with current anti-bot configuration
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get('title', 'Unknown')[:50]
                        duration = info.get('duration', 0)
                        
                    # Check if file was downloaded
                    files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
                    
                    if files:
                        file_path = os.path.join(temp_dir, files[0])
                        file_size = os.path.getsize(file_path)
                        
                        if file_size > 1024:  # At least 1KB
                            logger.info(f"✅ Anti-bot bypass successful on attempt {attempt}")
                            break
                    
                    # If we get here, the attempt failed
                    raise Exception(f"Attempt {attempt} failed - no valid file downloaded")
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    logger.warning(f"⚠️ Attempt {attempt} failed: {str(e)}")
                    
                    if attempt == max_attempts:
                        # All attempts failed
                        if 'sign in' in error_msg or 'bot' in error_msg:
                            raise Exception("YouTube bot detection could not be bypassed after all attempts")
                        elif 'private' in error_msg:
                            raise Exception("Video is private or restricted")
                        elif 'not available' in error_msg:
                            raise Exception("Video not available or removed")
                        else:
                            raise Exception(f"All {max_attempts} anti-bot attempts failed: {str(e)}")
                    
                    # Continue to next attempt
                    continue
            
            # Success - file downloaded
            if not files or file_size <= 1024:
                raise Exception("Download completed but no valid file found")
            
            # Check file size limit
            if file_size > 50 * 1024 * 1024:  # 50MB
                await status_msg.edit_text(
                    f"❌ **File Too Large**\n\n"
                    f"📁 **Size:** {file_size/(1024*1024):.1f} MB\n"
                    f"⚠️ **Telegram Limit:** 50 MB\n"
                    f"🎬 **Title:** {title}\n\n"
                    f"💡 **Try:** Shorter video or different quality",
                    parse_mode='Markdown'
                )
                return
            
            # Upload to Telegram
            await status_msg.edit_text(
                f"📤 **Uploading to Telegram**\n\n"
                f"📁 **Title:** {title}\n"
                f"📊 **Size:** {file_size/(1024*1024):.1f} MB\n"
                f"🎯 **Platform:** {platform}\n"
                f"✅ **Anti-bot:** Bypassed successfully!\n\n"
                f"⚡ **Almost ready...**",
                parse_mode='Markdown'
            )
            
            # Prepare caption
            duration_str = f"{duration//60}:{duration%60:02d}" if duration > 0 else "Unknown"
            
            caption = f"✅ **Anti-Bot Download Success!**\n\n"
            caption += f"📁 **Title:** {title}\n"
            caption += f"🎯 **Platform:** {platform}\n"
            caption += f"⏱️ **Duration:** {duration_str}\n"
            caption += f"📊 **Size:** {file_size/(1024*1024):.1f} MB\n"
            caption += f"🛡️ **Bot Detection:** Bypassed\n\n"
            if is_test:
                caption += f"🧪 **This was an anti-bot test**\n"
            caption += f"🤖 **AnyLink Bot** | ☁️ **Railway Cloud**"
            
            # Send video
            with open(file_path, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption=caption[:1024],
                    parse_mode='Markdown',
                    supports_streaming=True
                )
            
            # Success message
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Download Another", callback_data="start"),
                    InlineKeyboardButton("🧪 Test Again", callback_data="test")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await status_msg.edit_text(
                f"🎉 **Anti-Bot Success!**\n\n"
                f"✅ Successfully bypassed {platform} bot detection\n"
                f"📱 Video downloaded and sent\n"
                f"🛡️ Anti-detection method worked!\n\n"
                f"💡 **Send more URLs to test!**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"🎉 Anti-bot download successful for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Anti-bot download failed: {str(e)}")
            
            error_msg = str(e).lower()
            
            if 'bot detection' in error_msg or 'sign in' in error_msg:
                error_text = f"🛡️ **Anti-Bot Detection Failed**\n\n"
                error_text += f"YouTube's bot detection is very strong today.\n\n"
                error_text += f"**💡 What you can try:**\n"
                error_text += f"• Try a different YouTube video\n"
                error_text += f"• Try Instagram or TikTok instead\n"
                error_text += f"• Wait a few minutes and try again\n"
                error_text += f"• Some videos work better than others"
                
            elif 'private' in error_msg:
                error_text = f"🔒 **{platform}: Private Content**\n\n"
                error_text += f"This video is private or restricted.\n\n"
                error_text += f"**💡 Try:** Public videos only"
                
            elif 'not available' in error_msg:
                error_text = f"❌ **{platform}: Video Not Available**\n\n"
                error_text += f"Video may be removed or geo-restricted.\n\n"
                error_text += f"**💡 Try:** Different video or platform"
                
            else:
                error_text = f"🚫 **{platform}: Download Failed**\n\n"
                error_text += f"**Error:** `{str(e)[:100]}...`\n\n"
                error_text += f"**💡 Try:**\n"
                error_text += f"• Different video URL\n"
                error_text += f"• Different platform (Instagram/TikTok)\n"
                error_text += f"• Wait and try again later"
            
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Try Different URL", callback_data="start"),
                    InlineKeyboardButton("🧪 Test Bot", callback_data="test")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await status_msg.edit_text(
                error_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        finally:
            # Cleanup
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"🧹 Cleaned up temp directory")
                except Exception as e:
                    logger.warning(f"⚠️ Cleanup failed: {e}")
    
    def run(self):
        print("🛡️ Starting Anti-Bot Detection Bot...")
        print("📱 Ready to bypass bot detection!")
        print("🎯 Send any YouTube URL to test!")
        
        try:
            self.application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"❌ Bot failed: {e}")
            print(f"💥 ERROR: {e}")

if __name__ == "__main__":
    print("🛡️ ANTI-BOT DETECTION VERSION")
    
    try:
        bot = AntiBotDownloaderBot()
        bot.run()
    except Exception as e:
        print(f"💥 STARTUP FAILED: {e}")
        sys.exit(1)
