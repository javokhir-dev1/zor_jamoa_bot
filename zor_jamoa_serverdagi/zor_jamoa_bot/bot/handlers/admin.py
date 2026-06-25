"""
Admin handlerlari:
  - Arizani tasdiqlash / rad etish (callback)
  - /admin — admin panel bosh menyu
"""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.middlewares.admin import AdminOnly
from config import settings
from db.crud import get_user_by_id, update_user_status
from db.database import AsyncSessionLocal
from db.models import UserStatus

logger = logging.getLogger(__name__)
router = Router()
router.message.middleware(AdminOnly())
router.callback_query.middleware(AdminOnly())


# ---------------------------------------------------------------------------
# /admin — bosh menyu
# ---------------------------------------------------------------------------

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    from bot.keyboards.inline import admin_webapp_keyboard
    kb = admin_webapp_keyboard(settings.WEBAPP_URL) if settings.WEBAPP_URL else None
    await message.answer(
        "⚙️ <b>Admin panel</b>\n\n"
        "<b>Web App (tavsiya):</b> Quyidagi tugma orqali admin panelni oching.\n\n"
        "<b>Bot buyruqlari:</b>\n"
        "/pending — kutayotgan arizalar\n"
        "/add_user — hodimni qo'lda qo'shish\n"
        "/departments — bo'limlarni boshqarish\n"
        "/report — kunlik hisobot\n"
        "/distribute — ovqat tarqatish",
        reply_markup=kb,
    )


# ---------------------------------------------------------------------------
# Arizani tasdiqlash
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("admin_approve:"))
async def approve_user(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as db:
        user = await update_user_status(db, user_id, UserStatus.approved)

    if not user:
        await callback.answer("Foydalanuvchi topilmadi.", show_alert=True)
        return

    # Admin xabarini yangilash
    await callback.message.edit_text(
        callback.message.text + "\n\n✅ <b>Tasdiqlandi</b>"
    )

    # Foydalanuvchiga xabar
    from bot.keyboards.inline import webapp_keyboard
    try:
        await callback.bot.send_message(
            chat_id=user.telegram_id,
            text=(
                f"✅ <b>Tabriklaymiz, {user.full_name}!</b>\n\n"
                "Arizangiz tasdiqlandi. Endi ovqat buyurtma qilishingiz mumkin 🍽"
            ),
            reply_markup=webapp_keyboard(settings.WEBAPP_URL),
        )
    except Exception as e:
        logger.warning(f"Foydalanuvchi {user.telegram_id} ga xabar yuborib bo'lmadi: {e}")

    await callback.answer("✅ Tasdiqlandi")


# ---------------------------------------------------------------------------
# Arizani rad etish
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("admin_reject:"))
async def reject_user(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as db:
        user = await update_user_status(db, user_id, UserStatus.rejected)

    if not user:
        await callback.answer("Foydalanuvchi topilmadi.", show_alert=True)
        return

    await callback.message.edit_text(
        callback.message.text + "\n\n❌ <b>Rad etildi</b>"
    )

    try:
        await callback.bot.send_message(
            chat_id=user.telegram_id,
            text=(
                "❌ Afsuski, arizangiz rad etildi.\n"
                "Qo'shimcha ma'lumot uchun administratorga murojaat qiling."
            ),
        )
    except Exception as e:
        logger.warning(f"Foydalanuvchi {user.telegram_id} ga xabar yuborib bo'lmadi: {e}")

    await callback.answer("❌ Rad etildi")


# ---------------------------------------------------------------------------
# Kutayotgan arizalar ro'yxati
# ---------------------------------------------------------------------------

@router.message(Command("pending"))
async def cmd_pending(message: Message):
    from bot.keyboards.inline import approve_reject_keyboard
    from db.crud import get_pending_users

    async with AsyncSessionLocal() as db:
        users = await get_pending_users(db)

    if not users:
        await message.answer("✅ Kutayotgan ariza yo'q.")
        return

    await message.answer(f"📋 <b>Kutayotgan arizalar: {len(users)} ta</b>")

    for user in users:
        dept_name = user.department.name if user.department else "—"
        text = (
            f"👤 <b>{user.full_name}</b>\n"
            f"📱 {user.phone_number or '—'}\n"
            f"🏢 {dept_name}\n"
            f"🆔 <code>{user.telegram_id}</code>"
        )
        await message.answer(text, reply_markup=approve_reject_keyboard(user.id))
