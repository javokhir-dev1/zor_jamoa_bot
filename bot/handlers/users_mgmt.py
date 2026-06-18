"""
Hodimlarni boshqarish (faqat admin):
  /add_user  — hodimni qo'lda qo'shish
  /del_user  — hodimni o'chirish / bo'limdan chiqarish
  /user_info — hodim ma'lumotlari
"""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    admin_dept_list_keyboard,
    departments_keyboard,
    user_actions_keyboard,
)
from bot.middlewares.admin import AdminOnly
from bot.states import AddUserStates
from db.crud import (
    create_user,
    get_all_departments,
    get_department_by_id,
    get_user_by_id,
    get_user_by_telegram_id,
    update_user_status,
)
from db.database import AsyncSessionLocal
from db.models import UserRole, UserStatus

logger = logging.getLogger(__name__)
router = Router()
router.message.middleware(AdminOnly())
router.callback_query.middleware(AdminOnly())


# ---------------------------------------------------------------------------
# /add_user — hodimni qo'lda qo'shish
# ---------------------------------------------------------------------------

@router.message(Command("add_user"))
async def cmd_add_user(message: Message, state: FSMContext):
    await state.set_state(AddUserStates.waiting_telegram_id)
    await message.answer(
        "👤 <b>Hodimni qo'lda qo'shish</b>\n\n"
        "Hodimning Telegram ID sini kiriting.\n"
        "<i>Masalan: 123456789</i>"
    )


@router.message(AddUserStates.waiting_telegram_id, F.text)
async def add_user_telegram_id(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("⚠️ Telegram ID faqat raqamlardan iborat bo'lishi kerak.")
        return

    telegram_id = int(text)

    async with AsyncSessionLocal() as db:
        existing = await get_user_by_telegram_id(db, telegram_id)

    if existing:
        await message.answer(
            f"⚠️ Bu Telegram ID allaqachon ro'yxatda mavjud:\n"
            f"<b>{existing.full_name}</b> — {existing.status.value}",
            reply_markup=user_actions_keyboard(existing.id),
        )
        await state.clear()
        return

    await state.update_data(telegram_id=telegram_id)
    await state.set_state(AddUserStates.waiting_full_name)
    await message.answer("✏️ Ism-familiyasini kiriting:")


@router.message(AddUserStates.waiting_full_name, F.text)
async def add_user_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 3:
        await message.answer("⚠️ Ism juda qisqa. Qayta kiriting:")
        return
    await state.update_data(full_name=name)
    await state.set_state(AddUserStates.waiting_phone)
    await message.answer(
        "📱 Telefon raqamini kiriting (ixtiyoriy).\n"
        "O'tkazib yuborish uchun <b>/skip</b> yozing."
    )


@router.message(AddUserStates.waiting_phone, Command("skip"))
@router.message(AddUserStates.waiting_phone, F.text)
async def add_user_phone(message: Message, state: FSMContext):
    phone = None
    if message.text and not message.text.startswith("/skip"):
        phone = message.text.strip()
        if not phone.startswith("+"):
            phone = "+" + phone

    await state.update_data(phone=phone)

    async with AsyncSessionLocal() as db:
        depts = await get_all_departments(db)

    if not depts:
        await message.answer("⚠️ Hali bo'lim yo'q. Avval /departments orqali bo'lim qo'shing.")
        await state.clear()
        return

    await state.set_state(AddUserStates.waiting_dept)
    await message.answer(
        "🏢 Bo'limni tanlang:",
        reply_markup=departments_keyboard(depts),
    )


@router.callback_query(AddUserStates.waiting_dept, F.data.startswith("reg_dept:"))
async def add_user_dept(callback: CallbackQuery, state: FSMContext):
    dept_id = int(callback.data.split(":")[1])
    data = await state.get_data()

    async with AsyncSessionLocal() as db:
        dept = await get_department_by_id(db, dept_id)
        user = await create_user(
            db=db,
            telegram_id=data["telegram_id"],
            full_name=data["full_name"],
            phone_number=data.get("phone"),
            department_id=dept_id,
        )
        # Admin qo'shganida darhol tasdiqlash
        user = await update_user_status(db, user.id, UserStatus.approved)

    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>{user.full_name}</b> qo'shildi va tasdiqlandi.\n"
        f"🏢 Bo'lim: {dept.name}\n"
        f"🆔 Telegram ID: <code>{user.telegram_id}</code>"
    )

    # Hodimga xabar yuborish
    from bot.keyboards.inline import webapp_keyboard
    from config import settings
    try:
        await callback.bot.send_message(
            chat_id=user.telegram_id,
            text=(
                f"✅ <b>Xush kelibsiz, {user.full_name}!</b>\n\n"
                "Siz tizimga qo'shildingiz. Ovqat buyurtma qilishingiz mumkin 🍽"
            ),
            reply_markup=webapp_keyboard(settings.WEBAPP_URL),
        )
    except Exception as e:
        logger.warning(f"Hodim {user.telegram_id} ga xabar yuborib bo'lmadi: {e}")

    await callback.answer()


# ---------------------------------------------------------------------------
# Hodimni o'chirish (callback — inline tugma orqali)
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("user_delete:"))
async def user_delete_confirm(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    async with AsyncSessionLocal() as db:
        user = await get_user_by_id(db, user_id)

    if not user:
        await callback.answer("Hodim topilmadi.", show_alert=True)
        return

    from bot.keyboards.inline import confirm_keyboard
    await callback.message.edit_text(
        f"⚠️ <b>{user.full_name}</b> ni tizimdan o'chirishni tasdiqlaysizmi?",
        reply_markup=confirm_keyboard(f"user_del:{user_id}"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm:user_del:"))
async def user_delete_execute(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[2])

    async with AsyncSessionLocal() as db:
        user = await get_user_by_id(db, user_id)
        if not user:
            await callback.message.edit_text("⚠️ Hodim topilmadi.")
            await callback.answer()
            return
        name = user.full_name
        # Soft delete — rejected statusga o'tkazamiz
        await update_user_status(db, user_id, UserStatus.rejected)

    await callback.message.edit_text(f"🗑 <b>{name}</b> tizimdan chiqarildi.")
    await callback.answer()


# ---------------------------------------------------------------------------
# /user_info <telegram_id> — hodim ma'lumotlari
# ---------------------------------------------------------------------------

@router.message(Command("user_info"))
async def cmd_user_info(message: Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Ishlatish: <code>/user_info 123456789</code>")
        return

    telegram_id = int(args[1])
    async with AsyncSessionLocal() as db:
        user = await get_user_by_telegram_id(db, telegram_id)

    if not user:
        await message.answer("⚠️ Hodim topilmadi.")
        return

    dept_name = user.department.name if user.department else "—"
    role_map = {UserRole.employee: "Hodim", UserRole.dept_head: "Bo'lim rahbari", UserRole.admin: "Admin"}
    status_map = {UserStatus.pending: "⏳ Kutilmoqda", UserStatus.approved: "✅ Tasdiqlangan", UserStatus.rejected: "❌ Rad etilgan"}

    await message.answer(
        f"👤 <b>{user.full_name}</b>\n"
        f"📱 Telefon: {user.phone_number or '—'}\n"
        f"🏢 Bo'lim: {dept_name}\n"
        f"🎭 Rol: {role_map.get(user.role, user.role)}\n"
        f"📊 Holat: {status_map.get(user.status, user.status)}\n"
        f"🆔 Telegram ID: <code>{user.telegram_id}</code>\n"
        f"📅 Qo'shilgan: {user.created_at.strftime('%d.%m.%Y')}",
        reply_markup=user_actions_keyboard(user.id),
    )
