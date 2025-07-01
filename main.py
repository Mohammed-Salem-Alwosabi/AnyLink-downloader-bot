# main.py - DEBUG VERSION to find download issues
import os
import sys
import logging
import tempfile
import shutil
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re

# Hardcoded token for testing
BOT_TOKEN = "7838776856:AAErH9mZQX1j29803t98hE9YFcab8fUm-gk"

# Enhanced logging
logging.basicConfig(
    level=logging.DEBUG,  # More detailed logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

print("🔍 DEBUG MODE: Enhanced logging enabled")
print(f"🤖 Bot token: {BOT_TOKEN[:20]}...")
print("🚀 Starting DEBUG version of AnyLink Downloader Bot...")

# Check system environment
print("\n📊 SYSTEM ENVIRONMENT CHECK:")
print(f"🐍 Python version: {sys.version}")
print(f"📁 Current directory: {os.getcwd()}")
print(f"🌍 Environment variables: {len(os.environ)}")
print(f"💾 Temp directory: {tempfile.gettempdir()}")

class DebugBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
        self.check_dependencies()
        
    def check_dependencies(self):
        """Check all required dependencies and system tools"""
        print("\n🔍 DEPENDENCY CHECK:")
        
        # Check Python packages
        try:
            import telegram
            print("✅ python-telegram-bot: Available")
        except ImportError as e:
            print(f"❌ python-telegram-bot: MISSING - {e}")
            
        try:
            import yt_dlp
            print("✅ yt-dlp: Available")
            print(f"📦 yt-dlp version: {yt_dlp.version.__version__}")
        except ImportError as e:
            print(f"❌ yt-dlp: MISSING - {e}")
            return
            
        # Check FFmpeg
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ FFmpeg: Available")
                # Get first line which contains version
                version_line = result.stdout.split('\n')[0]
                print(f"📦 FFmpeg: {version_line}")
            else:
                print("❌ FFmpeg: Not working properly")
        except subprocess.TimeoutExpired:
            print("⏱️ FFmpeg: Timeout (may still work)")
        except FileNotFoundError:
            print("❌ FFmpeg: Not found in PATH")
        except Exception as e:
            print(f"⚠️ FFmpeg check error: {e}")
            
        # Check yt-dlp functionality
        print("\n🧪 TESTING YT-DLP:")
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                # Test with a very simple, known working video
                test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # Very short test video
                info = ydl.extract_info(test_url, download=False)
                if info:
                    print("✅ yt-dlp: Can extract video info")
                    print(f"📹 Test video title: {info.get('title', 'Unknown')[:50]}")
                else:
                    print("❌ yt-dlp: Cannot extract video info")
        except Exception as e:
            print(f"❌ yt-dlp test failed: {e}")
            logger.error(f"yt-dlp test error: {e}")
        
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("debug", self.debug_info))
        self.application.add_handler(CommandHandler("test", self.test_download))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error_handler)
        
    async def error_handler(self, update, context):
        logger.error(f"❌ ERROR HANDLER: {context.error}")
        print(f"💥 ERROR OCCURRED: {context.error}")
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ **DEBUG ERROR:**\n\n`{str(context.error)[:500]}`\n\nCheck Railway logs for details.",
                parse_mode='Markdown'
            )
    
    def is_valid_url(self, text):
        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://(?:www\.)?youtu\.be/[\w-]+',
            r'https?://[^\s]+',
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome = """🔍 **DEBUG VERSION - AnyLink Downloader**

This is a debug version to identify download issues.

**🧪 Debug Commands:**
• `/debug` - Show system information
• `/test` - Test download with known working URL
• Send any URL - Detailed download attempt with logs

**🎯 Send me a video URL to see detailed debug info!**

Example: `https://youtu.be/jNQXAC9IVRw`"""
        
        await update.message.reply_text(welcome, parse_mode='Markdown')
        logger.info(f"👤 User {update.effective_user.id} started debug bot")
        
    async def debug_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show system debug information"""
        debug_text = f"""🔍 **SYSTEM DEBUG INFO**

**🤖 Bot Status:**
• Token: {BOT_TOKEN[:20]}...
• Telegram API: Connected ✅

**🐍 Python Environment:**
• Version: {sys.version.split()[0]}
• Platform: {sys.platform}
• Directory: `{os.getcwd()}`

**📦 Dependencies:**"""

        # Check dependencies in real-time
        try:
            import yt_dlp
            debug_text += f"\n• yt-dlp: ✅ v{yt_dlp.version.__version__}"
        except:
            debug_text += "\n• yt-dlp: ❌ Missing"
            
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                debug_text += "\n• FFmpeg: ✅ Available"
            else:
                debug_text += "\n• FFmpeg: ❌ Not working"
        except:
            debug_text += "\n• FFmpeg: ❌ Not found"

        debug_text += f"""

**💾 Storage:**
• Temp dir: `{tempfile.gettempdir()}`
• Write access: {"✅" if os.access(tempfile.gettempdir(), os.W_OK) else "❌"}

**🌐 Network:**
• Railway environment detected
• Outbound connections: Likely allowed

**📊 Memory/CPU:**
• Available for processing

Send `/test` to test download functionality!"""
        
        await update.message.reply_text(debug_text, parse_mode='Markdown')
        
    async def test_download(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test download with a known working URL"""
        test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # Very short test video
        
        await update.message.reply_text(
            f"🧪 **TESTING DOWNLOAD**\n\n"
            f"Testing with: `{test_url}`\n"
            f"This is a 1-second test video.\n\n"
            f"⏳ Starting test...",
            parse_mode='Markdown'
        )
        
        await self.download_video_debug(update, context, test_url, is_test=True)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        
        if self.is_valid_url(text):
            await self.download_video_debug(update, context, text)
        else:
            await update.message.reply_text(
                "🤔 **Not a valid URL**\n\n"
                "Send me a video URL or use:\n"
                "• `/debug` - System info\n"
                "• `/test` - Test download\n\n"
                "Example URL: `https://youtu.be/jNQXAC9IVRw`",
                parse_mode='Markdown'
            )
    
    async def download_video_debug(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, is_test=False):
        """Download with extensive debugging"""
        user_id = update.effective_user.id
        
        print(f"\n🎬 STARTING DOWNLOAD DEBUG for user {user_id}")
        print(f"🔗 URL: {url}")
        print(f"🧪 Test mode: {is_test}")
        
        status_msg = await update.message.reply_text(
            f"🔍 **DEBUG DOWNLOAD {'TEST' if is_test else ''}**\n\n"
            f"🔗 URL: `{url[:60]}...`\n"
            f"⏳ Step 1: Checking dependencies...",
            parse_mode='Markdown'
        )
        
        temp_dir = None
        step = 1
        
        try:
            # Step 1: Check yt-dlp import
            step += 1
            await status_msg.edit_text(
                f"🔍 **DEBUG STEP {step}**\n\n"
                f"🔗 URL: `{url[:60]}...`\n"
                f"✅ Step 1: Dependencies OK\n"
                f"⏳ Step 2: Importing yt-dlp...",
                parse_mode='Markdown'
            )
            
            import yt_dlp
            logger.info("✅ yt-dlp imported successfully")
            
            # Step 3: Create temp directory
            step += 1
            await status_msg.edit_text(
                f"🔍 **DEBUG STEP {step}**\n\n"
                f"🔗 URL: `{url[:60]}...`\n"
                f"✅ Step 1-2: Dependencies OK\n"
                f"⏳ Step 3: Creating temp directory...",
                parse_mode='Markdown'
            )
            
            temp_dir = tempfile.mkdtemp()
            logger.info(f"✅ Temp directory created: {temp_dir}")
            print(f"📁 Temp directory: {temp_dir}")
            
            # Step 4: Configure yt-dlp
            step += 1
            await status_msg.edit_text(
                f"🔍 **DEBUG STEP {step}**\n\n"
                f"🔗 URL: `{url[:60]}...`\n"
                f"✅ Steps 1-3: Setup complete\n"
                f"⏳ Step 4: Configuring downloader...",
                parse_mode='Markdown'
            )
            
            # Very basic yt-dlp options for debugging
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'format': 'worst',  # Use worst quality for faster testing
                'noplaylist': True,
                'no_warnings': False,  # Show warnings
                'ignoreerrors': False,
                'verbose': True,  # Verbose output
            }
            
            logger.info(f"✅ yt-dlp options configured: {ydl_opts}")
            
            # Step 5: Extract info (test connectivity)
            step += 1
            await status_msg.edit_text(
                f"🔍 **DEBUG STEP {step}**\n\n"
                f"🔗 URL: `{url[:60]}...`\n"
                f"✅ Steps 1-4: Configuration OK\n"
                f"⏳ Step 5: Testing video info extraction...",
                parse_mode='Markdown'
            )
            
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)  # Don't download yet, just extract info
                    title = info.get('title', 'Unknown')
                    duration = info.get('duration', 0)
                    logger.info(f"✅ Video info extracted: {title}")
                    print(f"📹 Video title: {title}")
                    print(f"⏱️ Duration: {duration} seconds")
                except Exception as e:
                    logger.error(f"❌ Info extraction failed: {e}")
                    raise Exception(f"Cannot extract video info: {e}")
            
            # Step 6: Actual download
            step += 1
            await status_msg.edit_text(
                f"🔍 **DEBUG STEP {step}**\n\n"
                f"🔗 URL: `{url[:60]}...`\n"
                f"✅ Steps 1-5: Video info OK\n"
                f"📹 Title: {title[:30]}...\n"
                f"⏳ Step 6: Starting actual download...",
                parse_mode='Markdown'
            )
            
            # Now try the actual download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("🎯 Starting yt-dlp download...")
                print("🎯 Starting yt-dlp download...")
                
                result = ydl.download([url])  # This should download the file
                logger.info(f"✅ yt-dlp download completed with result: {result}")
                print(f"✅ Download result: {result}")
            
            # Step 7: Check downloaded files
            step += 1
            await status_msg.edit_text(
                f"🔍 **DEBUG STEP {step}**\n\n"
                f"🔗 URL: `{url[:60]}...`\n"
                f"✅ Steps 1-6: Download completed\n"
                f"📹 Title: {title[:30]}...\n"
                f"⏳ Step 7: Checking downloaded files...",
                parse_mode='Markdown'
            )
            
            files = os.listdir(temp_dir)
            logger.info(f"📁 Files in temp directory: {files}")
            print(f"📁 Files found: {files}")
            
            if not files:
                raise Exception("No files found after download - yt-dlp may have failed silently")
            
            # Find the video file
            video_files = [f for f in files if os.path.isfile(os.path.join(temp_dir, f))]
            if not video_files:
                raise Exception("No video files found in download directory")
                
            file_path = os.path.join(temp_dir, video_files[0])
            file_size = os.path.getsize(file_path)
            
            logger.info(f"📄 Video file: {video_files[0]}")
            logger.info(f"📊 File size: {file_size} bytes ({file_size/(1024*1024):.2f} MB)")
            print(f"📄 Video file: {video_files[0]}")
            print(f"📊 File size: {file_size} bytes")
            
            if file_size == 0:
                raise Exception("Downloaded file is empty (0 bytes)")
            
            # Step 8: Upload to Telegram
            step += 1
            await status_msg.edit_text(
                f"🔍 **DEBUG STEP {step}**\n\n"
                f"✅ Steps 1-7: File ready\n"
                f"📹 Title: {title[:30]}...\n"
                f"📊 Size: {file_size/(1024*1024):.1f} MB\n"
                f"⏳ Step 8: Uploading to Telegram...",
                parse_mode='Markdown'
            )
            
            # Check file size limit
            if file_size > 50 * 1024 * 1024:  # 50MB
                raise Exception(f"File too large: {file_size/(1024*1024):.1f} MB (max 50MB)")
            
            # Send the video
            caption = f"✅ **DEBUG SUCCESS!**\n\n"
            caption += f"📹 **Title:** {title[:50]}\n"
            caption += f"📊 **Size:** {file_size/(1024*1024):.1f} MB\n"
            caption += f"⏱️ **Duration:** {duration}s\n\n"
            if is_test:
                caption += f"🧪 **This was a test download**\n"
            caption += f"🔍 **All debug steps completed successfully!**"
            
            with open(file_path, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption=caption[:1024],
                    parse_mode='Markdown'
                )
            
            # Final success message
            await status_msg.edit_text(
                f"🎉 **DEBUG COMPLETE - SUCCESS!**\n\n"
                f"✅ All 8 steps completed successfully\n"
                f"📹 Video downloaded and sent\n"
                f"📊 Size: {file_size/(1024*1024):.1f} MB\n\n"
                f"🔍 **The download system is working!**\n"
                f"{'🧪 Test completed successfully!' if is_test else '💡 Try more URLs!'}",
                parse_mode='Markdown'
            )
            
            logger.info("🎉 DEBUG DOWNLOAD COMPLETED SUCCESSFULLY!")
            print("🎉 DEBUG DOWNLOAD COMPLETED SUCCESSFULLY!")
            
        except Exception as e:
            error_details = str(e)
            logger.error(f"❌ DEBUG DOWNLOAD FAILED at step {step}: {error_details}")
            print(f"💥 ERROR at step {step}: {error_details}")
            
            # Detailed error message
            await status_msg.edit_text(
                f"❌ **DEBUG FAILED at Step {step}**\n\n"
                f"🔗 URL: `{url[:60]}...`\n"
                f"💥 **Error:** `{error_details[:200]}{'...' if len(error_details) > 200 else ''}`\n\n"
                f"🔍 **What this means:**\n"
                f"The download process failed at step {step}.\n"
                f"Check Railway logs for full details.\n\n"
                f"💡 **Next steps:**\n"
                f"• Try `/test` with a different URL\n"
                f"• Check `/debug` for system status\n"
                f"• Report this error to developer",
                parse_mode='Markdown'
            )
            
        finally:
            # Cleanup
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"🧹 Cleaned up temp directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to clean temp directory: {e}")
    
    def run(self):
        print("\n🚀 STARTING DEBUG BOT...")
        print("📱 Ready for debug testing!")
        print("🔍 Send /debug for system info")
        print("🧪 Send /test for download test")
        print("🎬 Send any URL for detailed download debug")
        
        try:
            self.application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"❌ Bot failed to start: {e}")
            print(f"💥 CRITICAL ERROR: {e}")

if __name__ == "__main__":
    print("🔍 STARTING DEBUG MODE...")
    
    try:
        bot = DebugBot()
        bot.run()
    except Exception as e:
        print(f"💥 STARTUP FAILED: {e}")
        logger.error(f"Startup failed: {e}")
        sys.exit(1)
