import asyncio
import httpx
from typing import Any, Dict
from dotenv import load_dotenv
import os
from telebot.exceptions import TelegramAPIError
from .models import Message
load_dotenv()


class TelegramClient:
    BASE_URL = os.getenv("BASE_TELEGRAM_API_URL")

    def __init__(self, token: str, *, timeout: int = 10):
        self.token = token
        self._client = httpx.AsyncClient(timeout=timeout)

    async def _request(self, method: str, data: Dict[str, Any] | None = None):
        url = f"{self.BASE_URL}/bot{self.token}/{method}"
        r = await self._client.post(url, json=data or {})
        payload = r.json()

        if not payload.get('ok'):
            raise TelegramAPIError.from_payload(payload)

        return payload["result"]

    async def send_message(self, chat_id: int | str, text: str, **kw):
        await self._request("sendMessage", {"chat_id": chat_id, "text": text, **kw})
    
    async def get_last_message(self) -> Message:
        raw = (await self._request("getUpdates", {"limit": 1}))
        print(raw)
        return Message.model_validate(raw)

    async def close(self):
        await self._client.aclose()
    

async def demo():
    import time
    st = time.time()
    bot = TelegramClient(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    await bot.send_message("963539362", "hello teleliblite!")
    l_m = await bot.get_last_message()
    await bot.close()
    en = time.time()
    print(en - st)
    print(l_m)


if __name__ == "__main__":
    asyncio.run(demo())
                         
