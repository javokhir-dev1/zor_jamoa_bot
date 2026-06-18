from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.models import Department, User


def departments_keyboard(departments: list[Department]) -> InlineKeyboardMarkup:
    """Bo'limlar ro'yxati — inline tugmalar."""
    builder = InlineKeyboardBuilder()
    for dept in departments:
        builder.button(
            text=dept.name,
            callback_data=f"reg_dept:{dept.id}",
        )
    builder.adjust(2)  # 2 ta ustun
    return builder.as_markup()


def approve_reject_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Admin uchun: tasdiqlash / rad etish tugmalari."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"admin_approve:{user_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"admin_reject:{user_id}",
                ),
            ]
        ]
    )


def admin_dept_list_keyboard(departments: list[Department]) -> InlineKeyboardMarkup:
    """Admin uchun bo'limlar ro'yxati — boshqarish."""
    builder = InlineKeyboardBuilder()
    for dept in departments:
        builder.button(text=dept.name, callback_data=f"dept_manage:{dept.id}")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="➕ Yangi bo'lim", callback_data="dept_add"))
    return builder.as_markup()


def dept_actions_keyboard(dept_id: int) -> InlineKeyboardMarkup:
    """Bo'lim uchun amallar: tahrirlash, rahbar belgilash, o'chirish."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Nomini o'zgartir", callback_data=f"dept_edit:{dept_id}"),
                InlineKeyboardButton(text="👑 Rahbar belgilash", callback_data=f"dept_sethead:{dept_id}"),
            ],
            [
                InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"dept_delete:{dept_id}"),
                InlineKeyboardButton(text="◀️ Orqaga", callback_data="dept_back"),
            ],
        ]
    )


def dept_members_keyboard(users: list, dept_id: int) -> InlineKeyboardMarkup:
    """Bo'lim a'zolari — rahbar sifatida tanlash."""
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.button(
            text=f"👤 {user.full_name}",
            callback_data=f"dept_head_pick:{dept_id}:{user.id}",
        )
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="🚫 Rahbarni bekor qilish", callback_data=f"dept_head_pick:{dept_id}:0"))
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"dept_manage:{dept_id}"))
    return builder.as_markup()


def user_actions_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Hodim uchun amallar."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"admin_approve:{user_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin_reject:{user_id}"),
            ],
            [
                InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"user_delete:{user_id}"),
            ],
        ]
    )


def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    """Tasdiqlash / bekor qilish."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm:{action}"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data="confirm:cancel"),
            ]
        ]
    )


def webapp_keyboard(webapp_url: str) -> InlineKeyboardMarkup:
    """Tasdiqlangan foydalanuvchi uchun Web App ochish tugmasi."""
    from aiogram.types import WebAppInfo

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🍽 Ovqat buyurtma qilish",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ]
        ]
    )


def admin_webapp_keyboard(webapp_url: str) -> InlineKeyboardMarkup:
    """Admin uchun Web App ochish tugmasi (/admin yo'li bilan)."""
    from aiogram.types import WebAppInfo

    base = webapp_url.rstrip("/")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🍽 Ovqat buyurtma",
                    web_app=WebAppInfo(url=webapp_url),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ Admin panel",
                    web_app=WebAppInfo(url=f"{base}/admin"),
                ),
            ],
        ]
    )
