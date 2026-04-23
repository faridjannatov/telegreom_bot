import asyncio
import os
from dotenv import load_dotenv
from telegrambot import TechNewsBot

async def send_first_news():
    """Send the first batch of news to the channel"""
    
    # Загружаем переменные из .env файла
    load_dotenv()

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    CHANNEL_ID = os.getenv("CHANNEL_ID")

    if not all([TELEGRAM_BOT_TOKEN, NEWS_API_KEY, CHANNEL_ID]):
        print("Ошибка: Отсутствуют необходимые переменные окружения. Проверьте файл .env!")
        return

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
