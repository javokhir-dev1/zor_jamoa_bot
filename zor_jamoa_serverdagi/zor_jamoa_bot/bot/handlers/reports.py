"""
Hisobot va ovqat tarqatish handlerlari (faqat admin):
  /report          — kunlik buyurtmalar hisoboti (13:59 dan keyin)
  /distribute      — tarqatish boshqaruvi
"""
import logging
from collections import defaultdict

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.middlewares.admin import AdminOnly
from db.crud import get_all_departments, get_orders_by_date, mark_order_taken
from db.database import AsyncSessionLocal
from db.models import MealType

logger = logging.getLogger(__name__)
router = Router()
router.message.middleware(AdminOnly())
router.callback_query.middleware(AdminOnly())


# ---------------------------------------------------------------------------
# Yordamchi — hisobot matni shakllantirish
# ---------------------------------------------------------------------------

def _build_report_text(orders, report_date, is_final: bool) -> str:
    """Buyurtmalar ro'yxatidan formatlangan matn qaytaradi."""
    lunch_by_dept  = defaultdict(list)
    dinner_by_dept = defaultdict(list)

    for o in orders:
        dept = o.user.department.name if o.user.department else "Bo'limsiz"
        if o.meal_type == MealType.tushlik:
            lunch_by_dept[dept].append(o.user.full_name)
        else:
            dinner_by_dept[dept].append(o.user.full_name)

    lunch_total  = sum(len(v) for v in lunch_by_dept.values())
    dinner_total = sum(len(v) for v in dinner_by_dept.values())

    date_str = report_date.strftime("%d.%m.%Y")
    status_mark = "✅ Yakuniy" if is_final else "⏳ Joriy (to'liq emas)"

    lines = [
        f"📊 <b>Kunlik hisobot — {date_str}</b>",
        f"<i>{status_mark}</i>",
        "",
    ]

    # Tushlik
    lines.append(f"🍱 <b>Tushlik — jami: {lunch_total} ta</b>")
    if lunch_by_dept:
        for dept, names in sorted(lunch_by_dept.items()):
            lines.append(f"\n  <b>{dept}</b> ({len(names)} ta):")
            for name in names:
                lines.append(f"    • {name}")
    else:
        lines.append("  <i>Buyurtma yo'q</i>")

    lines.append("")

    # Kechki ovqat
    lines.append(f"🍽 <b>Kechki ovqat — jami: {dinner_total} ta</b>")
    if dinner_by_dept:
        for dept, names in sorted(dinner_by_dept.items()):
            lines.append(f"\n  <b>{dept}</b> ({len(names)} ta):")
            for name in names:
                lines.append(f"    • {name}")
    else:
        lines.append("  <i>Buyurtma yo'q</i>")

    lines += ["", f"<b>Jami: {lunch_total + dinner_total} ta buyurtma</b>"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# /report — kunlik hisobot
# ---------------------------------------------------------------------------

@router.message(Command("report"))
async def cmd_report(message: Message):
    from api.utils import is_report_ready, today_tashkent, tomorrow_tashkent

    # Argument sifatida sana berish mumkin: /report 2026-06-19
    args = message.text.split()
    if len(args) > 1:
        from datetime import date
        try:
            target = date.fromisoformat(args[1])
            is_final = True  # O'tgan kun — har doim yakuniy
        except ValueError:
            await message.answer("❌ Noto'g'ri sana. Misol: <code>/report 2026-06-19</code>")
            return
    else:
        target = tomorrow_tashkent()   # Hisobot ertangi kun uchun berilgan buyurtmalar
        is_final = is_report_ready()

    if not is_final and target == tomorrow_tashkent():
        await message.answer(
            "⏳ Kunlik hisobot <b>13:59</b> dan keyin tayyor bo'ladi.\n"
            "Hozirgi (to'liq bo'lmagan) hisobotni ko'rish uchun:\n"
            "<code>/report_now</code>"
        )
        return

    async with AsyncSessionLocal() as db:
        orders = await get_orders_by_date(db, target)

    if not orders:
        await message.answer(f"📭 {target.strftime('%d.%m.%Y')} uchun buyurtma yo'q.")
        return

    await message.answer(_build_report_text(orders, target, is_final))


@router.message(Command("report_now"))
async def cmd_report_now(message: Message):
    """Vaqtdan qat'iy nazar joriy holatni ko'rsatadi."""
    from api.utils import tomorrow_tashkent

    target = tomorrow_tashkent()
    async with AsyncSessionLocal() as db:
        orders = await get_orders_by_date(db, target)

    if not orders:
        await message.answer("📭 Hozircha buyurtma yo'q.")
        return

    await message.answer(_build_report_text(orders, target, is_final=False))


# ---------------------------------------------------------------------------
# /distribute — tarqatish boshqaruvi
# ---------------------------------------------------------------------------

@router.message(Command("distribute"))
async def cmd_distribute(message: Message):
    """Bo'lim tanlash — tarqatish ro'yxati."""
    async with AsyncSessionLocal() as db:
        depts = await get_all_departments(db)

    if not depts:
        await message.answer("Bo'limlar yo'q.")
        return

    builder_rows = []
    for d in depts:
        builder_rows.append([
            InlineKeyboardButton(
                text=d.name,
                callback_data=f"dist_dept:{d.id}",
            )
        ])

    await message.answer(
        "🏢 Qaysi bo'lim uchun tarqatishni boshlamoqchisiz?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=builder_rows),
    )


@router.callback_query(F.data.startswith("dist_dept:"))
async def dist_dept_selected(callback: CallbackQuery):
    """Bo'lim tanlandi — ovqat turi tanlash."""
    dept_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as db:
        from db.crud import get_department_by_id
        dept = await get_department_by_id(db, dept_id)

    if not dept:
        await callback.answer("Bo'lim topilmadi.", show_alert=True)
        return

    await callback.message.edit_text(
        f"🏢 <b>{dept.name}</b>\n\nQaysi ovqatni tarqatyapsiz?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🍱 Tushlik", callback_data=f"dist_list:{dept_id}:tushlik"),
                InlineKeyboardButton(text="🍽 Kechki ovqat", callback_data=f"dist_list:{dept_id}:kechki_ovqat"),
            ],
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="dist_back")],
        ]),
    )
    await callback.answer()


@router.callback_query(F.data == "dist_back")
async def dist_back(callback: CallbackQuery):
    async with AsyncSessionLocal() as db:
        depts = await get_all_departments(db)
    rows = [[InlineKeyboardButton(text=d.name, callback_data=f"dist_dept:{d.id}")] for d in depts]
    await callback.message.edit_text(
        "🏢 Bo'limni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("dist_list:"))
async def dist_list(callback: CallbackQuery):
    """Tarqatish ro'yxati — hodimlar va tugmalar."""
    _, dept_id_str, meal_str = callback.data.split(":")
    dept_id = int(dept_id_str)
    meal = MealType(meal_str)

    from api.utils import today_tashkent
    target = today_tashkent()

    async with AsyncSessionLocal() as db:
        orders = await get_orders_by_date(db, target)
        from db.crud import get_department_by_id
        dept = await get_department_by_id(db, dept_id)

    dept_orders = [
        o for o in orders
        if o.user.department_id == dept_id and o.meal_type == meal
    ]

    if not dept_orders:
        await callback.message.edit_text(
            f"📭 <b>{dept.name}</b> — bu ovqat uchun buyurtma yo'q.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"dist_dept:{dept_id}")
            ]]),
        )
        await callback.answer()
        return

    meal_label = "🍱 Tushlik" if meal == MealType.tushlik else "🍽 Kechki ovqat"
    taken  = [o for o in dept_orders if o.is_taken]
    pending = [o for o in dept_orders if not o.is_taken]

    text_lines = [
        f"<b>{dept.name}</b> — {meal_label}",
        f"Jami: {len(dept_orders)} ta | ✅ Oldi: {len(taken)} | ⏳ Olmadi: {len(pending)}",
        "",
    ]

    rows = []
    for o in dept_orders:
        status = "✅" if o.is_taken else "⬜"
        btn_text = f"{status} {o.user.full_name}"
        if not o.is_taken:
            rows.append([InlineKeyboardButton(
                text=btn_text,
                callback_data=f"dist_take:{o.id}:{dept_id}:{meal_str}",
            )])
        else:
            # Olganlar — bosilmaydi, faqat ko'rsatiladi
            rows.append([InlineKeyboardButton(text=btn_text, callback_data="dist_noop")])

    rows.append([InlineKeyboardButton(text="🔄 Yangilash", callback_data=f"dist_list:{dept_id}:{meal_str}")])
    rows.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"dist_dept:{dept_id}")])

    await callback.message.edit_text(
        "\n".join(text_lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )
    await callback.answer()


@router.callback_query(F.data == "dist_noop")
async def dist_noop(callback: CallbackQuery):
    await callback.answer("Bu hodim ovqatini allaqachon olgan ✅")


@router.callback_query(F.data.startswith("dist_take:"))
async def dist_take(callback: CallbackQuery):
    """'Buyurtma topshirildi' tugmasi."""
    parts = callback.data.split(":")
    order_id = int(parts[1])
    dept_id  = int(parts[2])
    meal_str = parts[3]

    async with AsyncSessionLocal() as db:
        order = await mark_order_taken(db, order_id)

    if not order:
        await callback.answer("Buyurtma topilmadi.", show_alert=True)
        return

    await callback.answer(f"✅ {order.user.full_name} — ovqat topshirildi!")

    # Ro'yxatni yangilash
    await dist_list.__wrapped__(callback) if hasattr(dist_list, "__wrapped__") else None

    # Sahifani yangilash uchun callback data ni qayta chaqiramiz
    callback.data = f"dist_list:{dept_id}:{meal_str}"
    await dist_list(callback)
