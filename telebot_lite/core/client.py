import os
import asyncio
import httpx
from typing import Any, Dict
from telebot_lite.core.exception import TelegramAPIError
from telebot_lite.db.models import Message, User, Chat


# Telegram Bot API Client
class TelegramClient:

    def __init__(self, token: str, *, timeout: int = 10, telegram_api_server: str = 'https://api.telegram.org'):
        """
        Set Token
        if run telegram api server please set like -> telegram_api_server = '127.0.0.1:8081'
        """
        self.token = token
        self.BASE_URL = telegram_api_server
        self._client = httpx.AsyncClient(timeout=timeout)

    async def _request(self, method: str, data: Dict[str, Any] | None = None, http_method: str = "POST"):
        url = f"{self.BASE_URL}/bot{self.token}/{method}"
        if http_method == "POST":
            r = await self._client.post(url, json=data or {})
        else:
            r = await self._client.get(url, params=data or {})

        payload = r.json()
        if not payload.get("ok"):
            raise TelegramAPIError.from_payload(payload)

        return payload["result"]

    async def send_message(self, chat_id: int | str, text: str, **kw):
        try:
            return await self._request("sendMessage", {"chat_id": chat_id, "text": text, **kw})
        except TelegramAPIError as e:
            print(f"Error sending message: {e}")
            return None

    async def get_last_message(self) -> Message | None:
        try:
            raw = await self._request("getUpdates", {"limit": 1})
            if raw:
                return Message.model_validate(raw[-1])
            return None
        except TelegramAPIError as e:
            print(f"Error fetching last message: {e}")
            return None

    async def set_webhook(self, url: str):
        try:
            data = {"url": url}
            return await self._request("setWebhook", data)
        except TelegramAPIError as e:
            print(f"Eraror setting webhook: {e}")
            return None

    async def delete_webhook(self):
        try:
            return await self._request("deleteWebhook")
        except TelegramAPIError as e:
            print(f"Error deleting webhook: {e}")
            return None
        
    async def process_update(self, update):
        message = update.get("message", {}).get("text", "")
        chat_id = update.get("message", {}).get("chat", {}).get("id", "")
        
        if message == "/start":
            await self.send_message(chat_id, "سلام! ممنون از پروژه telebot_lite پشتیبانی کردی. 🚀")
        else:
            await self.send_message(chat_id, f"شما گفتید: {message}")
            
    async def ask_for_contact(self, chat_id: int | str, message: str = "لطفاً شماره موبایل‌تان را ارسال کنید", text: str = "ارسال شماره 📱"):
        keyboard = {
            "keyboard": [[
                {
                    "text": text,
                    "request_contact": True
                }
            ]],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }

        return await self.send_message(
            chat_id,
            message,
            reply_markup=keyboard
        )

    async def close(self):
        await self._client.aclose()
