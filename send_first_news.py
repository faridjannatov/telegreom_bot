import asyncio
from telegrambot import TechNewsBot

async def send_first_news():
    """Send the first batch of news to the channel"""
    TELEGRAM_BOT_TOKEN = "8233708906:AAFTzVAIbSHWqED8KwK5sDqIlp-1cnOvfCM"
    NEWS_API_KEY = "68a8f3d2cc6e4930bf0e27b3ec581ccc"
    CHANNEL_ID = "@aygunsdailytechnews"

    # Create bot instance
    bot = TechNewsBot(
        telegram_token=TELEGRAM_BOT_TOKEN,
        news_api_key=NEWS_API_KEY,
        channel_id=CHANNEL_ID,
    )

    print("Fetching and sending first news to channel...")
    await bot.send_daily_news()
    print("News sent successfully!")

if __name__ == "__main__":
    asyncio.run(send_first_news())