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
            
    async def keyboard(
        self,
        chat_id: int | str,
        message: str,
        buttons: list[list[dict]],
        resize: bool = True,
        one_time: bool = False,
        delete_after: int = 0
    ):
        reply_markup = {
            "keyboard": buttons,
            "resize_keyboard": resize,
            "one_time_keyboard": one_time
        }

        if delete_after == 0:
            return await self.send_message(
                chat_id,
                message,
                reply_markup=reply_markup
            )
        else:
            return await self.send_and_delete(
                chat_id,
                message,
                delay=delete_after,
                reply_markup=reply_markup,
            )

            
    async def keyboard_inline(
        self,
        chat_id: int | str,
        message: str,
        buttons: list[list[dict]],
        delete_after: int = 0
    ):
        reply_markup = {
            "inline_keyboard": buttons
        }
        
        if delete_after == 0:

            return await self.send_message(
                chat_id,
                message,    
                reply_markup=reply_markup
            )
        else:
            return await self.send_and_delete(
                chat_id,
                message,
                delay=delete_after,
                reply_markup=reply_markup
            )


    async def close(self):
        await self._client.aclose()
        
    async def delete_message(self, chat_id: int | str, message_id: int):
        return await self._request("deleteMessage", {
            "chat_id": chat_id,
            "message_id": message_id,
        })
        
    async def send_and_delete(self, chat_id: int, text: str, delay: int = 10, **kwargs):
        msg = await self.send_message(chat_id, text, **kwargs)
        
        if kwargs.get("use_celery", False):
            from telebot_lite.utils.tasks.delete_task import delete_message_task
            delete_message_task.apply_async((chat_id, msg["message_id"]), countdown=delay)
        else:
            asyncio.create_task(self._delete_after(chat_id, msg["message_id"], delay))

    async def _delete_after(self, chat_id: int, message_id: int, delay: int):
        await asyncio.sleep(delay)
        try:
            await self.delete_message(chat_id, message_id)
        except Exception as e:
            print(f"❌ delete failed for {chat_id=} {message_id=}: {e}")
