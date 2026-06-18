"""
Bo'limlarni boshqarish (faqat admin):
  /departments — ro'yxat
  Yangi bo'lim qo'shish / nom tahrirlash / rahbar belgilash / o'chirish
"""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    admin_dept_list_keyboard,
    dept_actions_keyboard,
    dept_members_keyboard,
)
from bot.middlewares.admin import AdminOnly
from bot.states import DeptStates
from db.crud import (
    create_department,
    delete_department,
    get_all_departments,
    get_department_by_id,
    get_department_members,
    set_department_head,
)
from db.database import AsyncSessionLocal

logger = logging.getLogger(__name__)
router = Router()
router.message.middleware(AdminOnly())
router.callback_query.middleware(AdminOnly())


# ---------------------------------------------------------------------------
# /departments — ro'yxat
# ---------------------------------------------------------------------------

@router.message(Command("departments"))
async def cmd_departments(message: Message):
    async with AsyncSessionLocal() as db:
        depts = await get_all_departments(db)

    if not depts:
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        await message.answer(
            "📂 Hali bo'lim yo'q.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="➕ Yangi bo'lim", callback_data="dept_add")
            ]])
        )
        return

    lines = [f"📂 <b>Bo'limlar ro'yxati ({len(depts)} ta):</b>\n"]
    for d in depts:
        head = f" — Rahbar: <b>{d.head.full_name}</b>" if d.head else ""
        lines.append(f"• {d.name}{head}")

    await message.answer(
        "\n".join(lines),
        reply_markup=admin_dept_list_keyboard(depts),
    )


# ---------------------------------------------------------------------------
# Bo'lim tanlash → amallar
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("dept_manage:"))
async def dept_manage(callback: CallbackQuery):
    dept_id = int(callback.data.split(":")[1])
    async with AsyncSessionLocal() as db:
        dept = await get_department_by_id(db, dept_id)

    if not dept:
        await callback.answer("Bo'lim topilmadi.", show_alert=True)
        return

    head_info = f"\n👑 Rahbar: <b>{dept.head.full_name}</b>" if dept.head else "\n👑 Rahbar: belgilanmagan"
    await callback.message.edit_text(
        f"🏢 <b>{dept.name}</b>{head_info}\n\nNima qilmoqchisiz?",
        reply_markup=dept_actions_keyboard(dept_id),
    )
    await callback.answer()


@router.callback_query(F.data == "dept_back")
async def dept_back(callback: CallbackQuery):
    async with AsyncSessionLocal() as db:
        depts = await get_all_departments(db)
    await callback.message.edit_text(
        f"📂 <b>Bo'limlar ({len(depts)} ta):</b>",
        reply_markup=admin_dept_list_keyboard(depts),
    )
    await callback.answer()


# ---------------------------------------------------------------------------
# Yangi bo'lim qo'shish
# ---------------------------------------------------------------------------

@router.callback_query(F.data == "dept_add")
async def dept_add_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DeptStates.waiting_new_name)
    await callback.message.answer("✏️ Yangi bo'lim nomini kiriting:")
    await callback.answer()


@router.message(DeptStates.waiting_new_name, F.text)
async def dept_add_finish(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("⚠️ Nom juda qisqa. Qayta kiriting:")
        return

    async with AsyncSessionLocal() as db:
        existing = await get_all_departments(db)
        if any(d.name.lower() == name.lower() for d in existing):
            await message.answer(f"⚠️ <b>{name}</b> bo'limi allaqachon mavjud.")
            await state.clear()
            return
        dept = await create_department(db, name)

    await state.clear()
    await message.answer(f"✅ <b>{dept.name}</b> bo'limi qo'shildi.")


# ---------------------------------------------------------------------------
# Bo'lim nomini tahrirlash
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("dept_edit:"))
async def dept_edit_start(callback: CallbackQuery, state: FSMContext):
    dept_id = int(callback.data.split(":")[1])
    await state.update_data(editing_dept_id=dept_id)
    await state.set_state(DeptStates.waiting_edit_name)
    await callback.message.answer("✏️ Yangi nomni kiriting:")
    await callback.answer()


@router.message(DeptStates.waiting_edit_name, F.text)
async def dept_edit_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    dept_id = data["editing_dept_id"]
    new_name = message.text.strip()

    async with AsyncSessionLocal() as db:
        dept = await get_department_by_id(db, dept_id)
        if not dept:
            await message.answer("⚠️ Bo'lim topilmadi.")
            await state.clear()
            return
        old_name = dept.name
        dept.name = new_name
        await db.commit()

    await state.clear()
    await message.answer(f"✅ <b>{old_name}</b> → <b>{new_name}</b> o'zgartirildi.")


# ---------------------------------------------------------------------------
# Rahbar belgilash
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("dept_sethead:"))
async def dept_sethead_start(callback: CallbackQuery, state: FSMContext):
    dept_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as db:
        members = await get_department_members(db, dept_id)

    if not members:
        await callback.answer("Bu bo'limda tasdiqlangan hodim yo'q.", show_alert=True)
        return

    await state.update_data(sethead_dept_id=dept_id)
    await state.set_state(DeptStates.waiting_head_select)
    await callback.message.edit_text(
        "👑 Rahbar sifatida kimni belgilaysiz?",
        reply_markup=dept_members_keyboard(members, dept_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("dept_head_pick:"))
async def dept_head_pick(callback: CallbackQuery, state: FSMContext):
    _, dept_id_str, user_id_str = callback.data.split(":")
    dept_id = int(dept_id_str)
    user_id = int(user_id_str)  # 0 = rahbarni bekor qilish

    async with AsyncSessionLocal() as db:
        dept = await set_department_head(db, dept_id, user_id if user_id else None)

    await state.clear()

    if user_id == 0:
        await callback.message.edit_text(f"✅ <b>{dept.name}</b> bo'limining rahbari bekor qilindi.")
    else:
        async with AsyncSessionLocal() as db:
            from db.crud import get_user_by_id
            head = await get_user_by_id(db, user_id)
        await callback.message.edit_text(
            f"✅ <b>{dept.name}</b> bo'limiga rahbar: <b>{head.full_name}</b>"
        )
    await callback.answer()


# ---------------------------------------------------------------------------
# Bo'lim o'chirish
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("dept_delete:"))
async def dept_delete_confirm(callback: CallbackQuery):
    dept_id = int(callback.data.split(":")[1])
    async with AsyncSessionLocal() as db:
        dept = await get_department_by_id(db, dept_id)

    if not dept:
        await callback.answer("Bo'lim topilmadi.", show_alert=True)
        return

    from bot.keyboards.inline import confirm_keyboard
    await callback.message.edit_text(
        f"⚠️ <b>{dept.name}</b> bo'limini o'chirishni tasdiqlaysizmi?\n"
        "Bo'limdagi hodimlar bo'limsiz qoladi.",
        reply_markup=confirm_keyboard(f"dept_del:{dept_id}"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm:dept_del:"))
async def dept_delete_execute(callback: CallbackQuery):
    dept_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as db:
        dept = await get_department_by_id(db, dept_id)
        name = dept.name if dept else "—"
        ok = await delete_department(db, dept_id)

    if ok:
        await callback.message.edit_text(f"🗑 <b>{name}</b> bo'limi o'chirildi.")
    else:
        await callback.message.edit_text("⚠️ O'chirishda xatolik yuz berdi.")
    await callback.answer()


@router.callback_query(F.data == "confirm:cancel")
async def confirm_cancel(callback: CallbackQuery):
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.answer()
