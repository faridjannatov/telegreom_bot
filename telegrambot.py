import asyncio
import logging
from datetime import datetime, timedelta
import aiohttp
import json
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import schedule
import time
import threading

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class TechNewsBot:
    def __init__(self, telegram_token, news_api_key, channel_id):
        """
        Initialize the Tech News Bot

        Args:
            telegram_token (str): Your Telegram Bot Token from @BotFather
            news_api_key (str): Your News API key from newsapi.org
            channel_id (str): Your Telegram channel ID (e.g., "@yourchannel" or "-100123456789")
        """
        self.telegram_token = telegram_token
        self.news_api_key = news_api_key
        self.channel_id = channel_id
        self.bot = Bot(token=telegram_token)
        self.application = Application.builder().token(telegram_token).build()

        # Tech news sources including Korean and international sources
        self.tech_sources = [
            "techcrunch",
            "the-verge",
            "wired",
            "ars-technica",
            "engadget",
            "venturebeat",
            "recode",
            "mashable",
            "reuters",
            "bbc-technology",
            "hacker-news",
            "the-next-web",
        ]

        # Korean tech sites and keywords for broader search
        self.korean_keywords = [
            "Samsung",
            "LG",
            "SK Hynix",
            "Kakao",
            "Naver",
            "Korea tech",
            "Korean startup",
            "Seoul",
            "K-tech",
            "Hyundai tech",
        ]

        self.tech_keywords = [
            "blockchain",
            "cryptocurrency",
            "NFT",
            "smart contract",
            "web3",
            "DeFi",
            "crypto",
            "Bitcoin",
            "Ethereum",
            "altcoin",
            "metaverse",
            "decentralized",
            "AI",
            "artificial intelligence",
            "machine learning",
            "startup",
            "technology",
            "software",
            "hardware",
            "mobile",
            "cloud computing",
            "cybersecurity",
            "semiconductor",
            "5G",
            "IoT",
            "robotics",
            "fintech",
            "electric vehicle",
            "autonomous",
        ]

    async def fetch_tech_news(self, limit=10):
        """
        Fetch latest tech news from News API including Korean and international tech news

        Args:
            limit (int): Number of articles to fetch

        Returns:
            list: List of news articles
        """
        try:
            # Calculate date for last 2 days to get more recent news
            two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

            # News API endpoint for everything
            url = "https://newsapi.org/v2/everything"

            all_articles = []

            # First query: General tech news with Korean keywords
            korean_query = " OR ".join(self.korean_keywords)
            general_query = " OR ".join(self.tech_keywords[:10])  # Limit keywords to avoid URL length issues

            queries = [
                f"({korean_query}) AND technology",
                f"({general_query}) AND (Korea OR Korean OR Seoul)",
                f"blockchain OR cryptocurrency OR NFT OR smart contract OR web3 OR DeFi",
                f"technology AND (startup OR AI OR semiconductor OR 5G)",
            ]

            for query in queries:
                params = {
                    "apiKey": self.news_api_key,
                    "q": query,
                    "sources": ",".join(self.tech_sources),
                    "from": two_days_ago,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "pageSize": limit // len(queries) + 2,
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            articles = data.get("articles", [])
                            all_articles.extend(articles)
                        else:
                            logger.error(f"Failed to fetch news for query '{query}': {response.status}")

            # Remove duplicates based on title and URL
            seen = set()
            unique_articles = []
            for article in all_articles:
                article_id = (article.get("title", ""), article.get("url", ""))
                if article_id not in seen and article.get("title") and article.get("url"):
                    seen.add(article_id)
                    unique_articles.append(article)

            # Sort by published date (most recent first)
            unique_articles.sort(
                key=lambda x: x.get("publishedAt", ""), reverse=True
            )

            return unique_articles[:limit]

        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []

    def format_news_message(self, articles):
        """
        Format news articles into a Telegram message

        Args:
            articles (list): List of news articles

        Returns:
            str: Formatted message
        """
        if not articles:
            return "🤖 No tech news found for today. Check back later!"

        message = (
            f"🚀 **Tech News Digest** - {datetime.now().strftime('%B %d, %Y')}\n\n"
        )

        for i, article in enumerate(
            articles[:8], 1
        ):  # Limit to 8 articles to avoid message length issues
            title = article.get("title", "No Title")
            url = article.get("url", "")
            source = article.get("source", {}).get("name", "Unknown")

            # Clean title (remove source name if it's at the end)
            if source in title:
                title = title.replace(f" - {source}", "").replace(f" | {source}", "")

            # Truncate title if too long
            if len(title) > 80:
                title = title[:80] + "..."

            message += f"{i}. **{title}**\n"
            message += f"   📰 _{source}_\n"
            if url:
                message += f"   🔗 [Read More]({url})\n"
            message += "\n"

        message += "---\n"
        message += "🤖 Powered by Tech News Bot | Updated every 3 hours with Korean & International IT news"

        return message

    async def send_daily_news(self):
        """
        Fetch and send daily tech news to the channel
        """
        try:
            logger.info("Fetching daily tech news...")
            articles = await self.fetch_tech_news(limit=10)

            if articles:
                message = self.format_news_message(articles)
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=message,
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                )
                logger.info(f"Sent {len(articles)} articles to channel")
            else:
                logger.warning("No articles found to send")

        except Exception as e:
            logger.error(f"Error sending daily news: {str(e)}")

    async def start_command(self, update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🤖 **Tech News Bot Started!**\n\n"
            "This bot sends daily tech news updates.\n\n"
            "**Commands:**\n"
            "/start - Start the bot\n"
            "/news - Get latest tech news now\n"
            "/help - Show help message",
            parse_mode="Markdown",
        )

    async def news_command(self, update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /news command - send latest news immediately"""
        await update.message.reply_text("🔄 Fetching latest tech news...")

        articles = await self.fetch_tech_news(limit=8)
        message = self.format_news_message(articles)

        await update.message.reply_text(
            message, parse_mode="Markdown", disable_web_page_preview=True
        )

    async def help_command(self, update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **Tech News Bot Help**

This bot automatically sends daily tech news updates at 9:00 AM.

**Commands:**
/start - Initialize the bot
/news - Get latest tech news immediately
/help - Show this help message

**Features:**
• Automated news every 3 hours (6AM, 9AM, 12PM, 3PM, 6PM, 9PM)
• Korean tech news (Samsung, LG, Kakao, Naver, Korean startups)
• International sources: TechCrunch, The Verge, Wired, Reuters, BBC Tech
• Focus on blockchain, crypto, NFT, smart contracts, AI, and emerging tech

**Setup:**
1. Add this bot to your channel as an admin
2. The bot will start sending daily updates automatically

Need help? Contact the bot administrator.
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")

    def schedule_news_updates(self):
        """Schedule frequent news updates throughout the day"""
        def send_news_sync():
            """Wrapper function to run async send_daily_news in sync context"""
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.send_daily_news())
                loop.close()
            except Exception as e:
                logger.error(f"Error in scheduled news update: {str(e)}")

        # Schedule news every 3 hours starting from 6 AM
        schedule.every().day.at("06:00").do(send_news_sync)
        schedule.every().day.at("09:00").do(send_news_sync)
        schedule.every().day.at("12:00").do(send_news_sync)
        schedule.every().day.at("15:00").do(send_news_sync)
        schedule.every().day.at("18:00").do(send_news_sync)
        schedule.every().day.at("21:00").do(send_news_sync)

        # Run scheduler in a separate thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

    def run(self):
        """
        Start the bot
        """
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("news", self.news_command))
        self.application.add_handler(CommandHandler("help", self.help_command))

        # Schedule frequent news updates
        self.schedule_news_updates()

        logger.info("Tech News Bot started! Scheduled to send news every 3 hours (6AM, 9AM, 12PM, 3PM, 6PM, 9PM) with Korean & International IT news")

        # Start the bot
        self.application.run_polling(drop_pending_updates=True)


# Example usage and configuration
if __name__ == "__main__":
    # Configuration - Replace these with your actual values
    TELEGRAM_BOT_TOKEN = (
        "8233708906:AAFTzVAIbSHWqED8KwK5sDqIlp-1cnOvfCM"  # Get from @BotFather
    )
    NEWS_API_KEY = "68a8f3d2cc6e4930bf0e27b3ec581ccc"  # Get from https://newsapi.org/
    CHANNEL_ID = "@aygunsdailytechnews"  # Your channel username or ID

    # Create and run the bot
    tech_news_bot = TechNewsBot(
        telegram_token=TELEGRAM_BOT_TOKEN,
        news_api_key=NEWS_API_KEY,
        channel_id=CHANNEL_ID,
    )

    try:
        tech_news_bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
