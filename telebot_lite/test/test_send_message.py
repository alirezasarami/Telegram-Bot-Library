from telebot_lite.core.client import TelegramClient
import asyncio
import os
from dotenv import load_dotenv
load_dotenv() 

async def demo():
    bot = TelegramClient(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    await bot.send_message(123456789, "سلام دنیا 👋")
    await bot.close()

if __name__ == "__main__":
    asyncio.run(demo())