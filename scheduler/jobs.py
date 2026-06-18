"""
Scheduled job funksiyalari.
APScheduler bu funksiyalarni belgilangan vaqtlarda chaqiradi.
"""
import logging
from collections import defaultdict

from aiogram import Bot

from config import settings
from db.crud import get_users_without_orders, get_orders_by_date
from db.database import AsyncSessionLocal
from db.models import MealType

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Eslatma jobi (12:00 – 13:50)
# ---------------------------------------------------------------------------

async def send_reminders(bot: Bot, reminder_num: int) -> None:
    """Hali buyurtma bermagan tasdiqlangan xodimlarga eslatma yuboradi."""
    from api.utils import tomorrow_tashkent

    target_date = tomorrow_tashkent()

    async with AsyncSessionLocal() as db:
        users = await get_users_without_orders(db, target_date)

    if not users:
        logger.info(f"Eslatma #{reminder_num}: hamma buyurtma bergan.")
        return

    logger.info(f"Eslatma #{reminder_num}: {len(users)} ta foydalanuvchiga yuborilmoqda.")

    text = (
        "🍽 <b>Eslatma!</b>\n\n"
        "Ertangi kun uchun ovqat buyurtma qilishni unutmang!\n"
        "Buyurtma <b>13:55</b> da yopiladi."
    )

    ok = fail = 0
    for user in users:
        try:
            await bot.send_message(chat_id=user.telegram_id, text=text)
            ok += 1
        except Exception as e:
            fail += 1
            logger.warning(f"Eslatma yuborib bo'lmadi → {user.telegram_id}: {e}")

    logger.info(f"Eslatma #{reminder_num}: yuborildi={ok}, xato={fail}")


# ---------------------------------------------------------------------------
# 20:00 yakuniy hisobot jobi
# ---------------------------------------------------------------------------

async def send_final_distribution_report(bot: Bot) -> None:
    """
    20:00 da adminlarga 'olgan / olmagan' yakuniy ro'yxatini yuboradi.
    """
    from api.utils import today_tashkent

    target = today_tashkent()

    async with AsyncSessionLocal() as db:
        orders = await get_orders_by_date(db, target)

    if not orders:
        logger.info("Yakuniy hisobot: buyurtma yo'q, yuborilmaydi.")
        return

    taken_by_dept   = defaultdict(list)
    missing_by_dept = defaultdict(list)

    for o in orders:
        dept = o.user.department.name if o.user.department else "Bo'limsiz"
        meal = "🍱" if o.meal_type == MealType.tushlik else "🍽"
        entry = f"{meal} {o.user.full_name}"
        if o.is_taken:
            taken_by_dept[dept].append(entry)
        else:
            missing_by_dept[dept].append(entry)

    date_str = target.strftime("%d.%m.%Y")
    total    = len(orders)
    n_taken  = sum(len(v) for v in taken_by_dept.values())
    n_miss   = sum(len(v) for v in missing_by_dept.values())

    lines = [
        f"📋 <b>Yakuniy tarqatish hisoboti — {date_str}</b>",
        f"Jami: {total} | ✅ Oldi: {n_taken} | ❌ Olmadi: {n_miss}",
        "",
    ]

    if taken_by_dept:
        lines.append("✅ <b>Ovqatini olganlar:</b>")
        for dept, entries in sorted(taken_by_dept.items()):
            lines.append(f"\n  <b>{dept}</b>:")
            lines.extend(f"    • {e}" for e in entries)
        lines.append("")

    if missing_by_dept:
        lines.append("❌ <b>Buyurtma berib, olmagan holatlar:</b>")
        for dept, entries in sorted(missing_by_dept.items()):
            lines.append(f"\n  <b>{dept}</b>:")
            lines.extend(f"    • {e}" for e in entries)

    text = "\n".join(lines)

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=text)
        except Exception as e:
            logger.warning(f"Admin {admin_id} ga hisobot yuborib bo'lmadi: {e}")

    logger.info(f"Yakuniy hisobot yuborildi: {n_taken} oldi, {n_miss} olmadi.")
