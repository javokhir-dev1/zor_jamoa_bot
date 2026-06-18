from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from config import settings
from db.crud import get_user_by_telegram_id
from db.database import AsyncSessionLocal
from db.models import UserRole


class AdminOnly(BaseMiddleware):
    """ADMIN_IDS yoki DB role=admin bo'lgan foydalanuvchilarga ruxsat beradi."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = None

        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        # .env ADMIN_IDS ni tekshir
        if user_id in settings.ADMIN_IDS:
            return await handler(event, data)

        # DB dagi rolni tekshir
        if user_id:
            async with AsyncSessionLocal() as db:
                user = await get_user_by_telegram_id(db, user_id)
            if user and user.role == UserRole.admin:
                return await handler(event, data)

        if isinstance(event, Message):
            await event.answer("⛔ Bu buyruq faqat adminlar uchun.")
        elif isinstance(event, CallbackQuery):
            await event.answer("⛔ Ruxsat yo'q.", show_alert=True)
