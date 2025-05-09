from telebot_lite.core.client import TelegramClient
import asyncio
import os
from dotenv import load_dotenv
load_dotenv() 

async def demo():
    bot = TelegramClient(token=os.getenv("TELEGRAM_BOT_TOKEN"), telegram_api_server='http://127.0.0.1:8081')
    await bot.send_message(963539362, "سلام دنیا 👋")
    await bot.close()

if __name__ == "__main__":
    asyncio.run(demo())