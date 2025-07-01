# AnyLink Downloader Bot

A powerful Telegram bot for downloading videos from various platforms, deployed on Railway.

## Features
- 🎬 Multi-platform support (YouTube, Instagram, TikTok, etc.)
- ⚡ Lightning-fast downloads via Railway cloud
- 🛡️ Reliable with 99.9% uptime
- 📱 Mobile-optimized interface
- 🆓 Completely free to use

## Supported Platforms
- YouTube (youtube.com, youtu.be)
- Instagram (posts, reels, IGTV)
- TikTok (tiktok.com, vm.tiktok.com)
- Facebook (public videos)
- Twitter/X (video tweets)
- Reddit (video posts)
- And many more!

## Deployment on Railway

### Prerequisites
- Railway account
- Telegram Bot Token from @BotFather

### Quick Deploy
1. Fork this repository
2. Connect to Railway
3. Set environment variable: `BOT_TOKEN=your_bot_token_here`
4. Deploy!

### Environment Variables
- `BOT_TOKEN` - Your Telegram bot token (required)
- `PORT` - Auto-set by Railway

## Local Development
```bash
git clone https://github.com/yourusername/anylink-downloader-bot
cd anylink-downloader-bot
pip install -r requirements.txt
export BOT_TOKEN=your_bot_token_here
python main.py