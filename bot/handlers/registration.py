"""
Ro'yxatdan o'tish oqimi:
  /start → telefon → ism-familiya → bo'lim tanlash → pending
"""
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import departments_keyboard
from bot.keyboards.reply import phone_keyboard, remove_keyboard
from bot.states import RegistrationStates
from config import settings
from db.crud import (
    create_user,
    get_all_departments,
    get_department_by_id,
    get_user_by_telegram_id,
)
from db.database import AsyncSessionLocal
from db.models import UserStatus

logger = logging.getLogger(__name__)
router = Router()


# ---------------------------------------------------------------------------
# /start
# ---------------------------------------------------------------------------

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    async with AsyncSessionLocal() as db:
        user = await get_user_by_telegram_id(db, message.from_user.id)

    if user:
        if user.status == UserStatus.approved:
            from bot.keyboards.inline import webapp_keyboard
            await message.answer(
                f"Xush kelibsiz, <b>{user.full_name}</b>! 👋\n"
                "Quyidagi tugma orqali ovqat buyurtma qilishingiz mumkin.",
                reply_markup=webapp_keyboard(settings.WEBAPP_URL),
            )
        elif user.status == UserStatus.pending:
            await message.answer(
                "⏳ Arizangiz ko'rib chiqilmoqda. "
                "Moderator tasdiqlashi bilan xabar beramiz."
            )
        else:  # rejected
            await message.answer(
                "❌ Arizangiz rad etilgan. "
                "Qo'shimcha ma'lumot uchun administratorga murojaat qiling."
            )
        return

    # Yangi foydalanuvchi — ro'yxatdan o'tish boshlash
    await state.set_state(RegistrationStates.waiting_phone)
    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "Zoʻr Jamoa imkoniyatlaridan toʻliq foydalanish va taom buyurtma qilish uchun "
        "pastdagi tugma orqali raqamingizni yuboring!",
        reply_markup=phone_keyboard(),
    )


# ---------------------------------------------------------------------------
# Telefon raqami
# ---------------------------------------------------------------------------

@router.message(RegistrationStates.waiting_phone, F.contact)
async def handle_phone(message: Message, state: FSMContext):
    # Faqat o'z kontaktini yuborishi kerak
    if message.contact.user_id != message.from_user.id:
        await message.answer(
            "⚠️ Iltimos, faqat o'z telefon raqamingizni yuboring.",
            reply_markup=phone_keyboard(),
        )
        return

    phone = message.contact.phone_number
    # +998 formatga keltirish
    if not phone.startswith("+"):
        phone = "+" + phone

    await state.update_data(phone=phone)
    await state.set_state(RegistrationStates.waiting_name)
    await message.answer(
        "Ro'yxatdan o'tish uchun ism va familiyangizni to'liq va to'g'ri yozing.",
        reply_markup=remove_keyboard(),
    )


@router.message(RegistrationStates.waiting_phone)
async def handle_phone_wrong(message: Message):
    await message.answer(
        "⚠️ Iltimos, tugma orqali telefon raqamingizni yuboring.",
        reply_markup=phone_keyboard(),
    )


# ---------------------------------------------------------------------------
# Ism-familiya
# ---------------------------------------------------------------------------

@router.message(RegistrationStates.waiting_name, F.text)
async def handle_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 3:
        await message.answer("⚠️ Iltimos, to'liq ism va familiyangizni kiriting.")
        return
    if len(name) > 200:
        await message.answer("⚠️ Ism juda uzun. Iltimos, qayta kiriting.")
        return

    await state.update_data(full_name=name)

    # Bo'limlar ro'yxatini yuklash
    async with AsyncSessionLocal() as db:
        departments = await get_all_departments(db)

    if not departments:
        await message.answer(
            "⚠️ Hozircha bo'limlar kiritilmagan. "
            "Iltimos, administratorga murojaat qiling."
        )
        await state.clear()
        return

    await state.set_state(RegistrationStates.waiting_dept)
    await message.answer(
        "Yo'nalishingizni tanlang 👇",
        reply_markup=departments_keyboard(departments),
    )


@router.message(RegistrationStates.waiting_name)
async def handle_name_wrong(message: Message):
    await message.answer("⚠️ Iltimos, ism-familiyangizni matn ko'rinishida yuboring.")


# ---------------------------------------------------------------------------
# Bo'lim tanlash (callback)
# ---------------------------------------------------------------------------

@router.callback_query(
    RegistrationStates.waiting_dept, F.data.startswith("reg_dept:")
)
async def handle_dept_selection(callback: CallbackQuery, state: FSMContext):
    dept_id = int(callback.data.split(":")[1])
    data = await state.get_data()

    async with AsyncSessionLocal() as db:
        dept = await get_department_by_id(db, dept_id)
        if not dept:
            await callback.answer("Bo'lim topilmadi. Qayta urinib ko'ring.", show_alert=True)
            return

        user = await create_user(
            db=db,
            telegram_id=callback.from_user.id,
            full_name=data["full_name"],
            phone_number=data.get("phone"),
            department_id=dept_id,
        )

    await state.clear()
    await callback.message.edit_text(
        "✅ Ro'yxatdan o'tish bo'yicha so'rovingiz qabul qilindi.\n\n"
        "Agar barcha ma'lumotlar to'g'ri bo'lsa, tez orada moderatorlar sizga "
        "Zoʻr Jamoa imkoniyatlaridan foydalanish uchun ruxsat berishadi."
    )

    # Adminlarga xabarnoma yuborish
    await _notify_admins(callback.bot, user, dept.name)
    await callback.answer()


async def _notify_admins(bot, user, dept_name: str):
    """Barcha adminlarga yangi ariza haqida xabar yuborish."""
    from bot.keyboards.inline import approve_reject_keyboard

    text = (
        "🆕 <b>Yangi ro'yxatdan o'tish arizasi</b>\n\n"
        f"👤 <b>Ism:</b> {user.full_name}\n"
        f"📱 <b>Telefon:</b> {user.phone_number or '—'}\n"
        f"🏢 <b>Bo'lim:</b> {dept_name}\n"
        f"🆔 <b>Telegram ID:</b> <code>{user.telegram_id}</code>"
    )

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=text,
                reply_markup=approve_reject_keyboard(user.id),
            )
        except Exception as e:
            logger.warning(f"Admin {admin_id} ga xabar yuborib bo'lmadi: {e}")
