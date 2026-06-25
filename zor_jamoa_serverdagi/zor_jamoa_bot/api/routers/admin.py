"""
Admin REST API — barcha admin operatsiyalar.
Faqat role=admin foydalanuvchilar uchun.
"""
import logging
from datetime import date
from typing import Optional

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from api.auth import get_admin_user
from config import settings

logger = logging.getLogger(__name__)


async def _notify(telegram_id: int, text: str, reply_markup=None) -> None:
    """Foydalanuvchiga Telegram xabar yuboradi (xatolik bo'lsa log qiladi)."""
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        await bot.send_message(chat_id=telegram_id, text=text, reply_markup=reply_markup)
    except Exception as e:
        logger.warning(f"Telegram xabar yuborilmadi {telegram_id}: {e}")
    finally:
        await bot.session.close()
from api.utils import is_report_ready, tomorrow_tashkent, today_tashkent
from db.crud import (
    create_department,
    create_user,
    delete_department,
    get_all_departments,
    get_department_by_id,
    get_department_members,
    get_order,
    get_orders_by_date,
    get_pending_users,
    get_user_by_id,
    get_user_by_telegram_id,
    mark_order_taken,
    set_department_head,
    update_user_role,
    update_user_status,
)
from db.database import AsyncSessionLocal
from db.models import MealType, User, UserRole, UserStatus

router = APIRouter()


# ===========================================================================
# 5.1 Arizalar
# ===========================================================================

@router.get("/applications")
async def get_applications(admin: User = Depends(get_admin_user)):
    async with AsyncSessionLocal() as db:
        users = await get_pending_users(db)
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "phone_number": u.phone_number,
            "telegram_id": u.telegram_id,
            "department": u.department.name if u.department else None,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.post("/applications/{user_id}/approve")
async def approve_application(user_id: int, admin: User = Depends(get_admin_user)):
    async with AsyncSessionLocal() as db:
        user = await update_user_status(db, user_id, UserStatus.approved)
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    from bot.keyboards.inline import webapp_keyboard
    await _notify(
        user.telegram_id,
        f"✅ <b>Tabriklaymiz, {user.full_name}!</b>\n\n"
        "Arizangiz tasdiqlandi. Endi ovqat buyurtma qilishingiz mumkin 🍽",
        reply_markup=webapp_keyboard(settings.WEBAPP_URL),
    )
    return {"ok": True}


@router.post("/applications/{user_id}/reject")
async def reject_application(user_id: int, admin: User = Depends(get_admin_user)):
    async with AsyncSessionLocal() as db:
        user = await update_user_status(db, user_id, UserStatus.rejected)
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    await _notify(
        user.telegram_id,
        "❌ Afsuski, arizangiz rad etildi.\n"
        "Qo'shimcha ma'lumot uchun administratorga murojaat qiling.",
    )
    return {"ok": True}


# ===========================================================================
# 5.2 Hodimlar
# ===========================================================================

@router.get("/users")
async def get_users(
    status: Optional[str] = Query(None),
    dept_id: Optional[int] = Query(None),
    admin: User = Depends(get_admin_user),
):
    from sqlalchemy import select
    from db.models import User as UserModel

    async with AsyncSessionLocal() as db:
        from sqlalchemy.orm import selectinload
        from sqlalchemy import and_

        q = select(UserModel).options(selectinload(UserModel.department))
        filters = []
        if status:
            try:
                filters.append(UserModel.status == UserStatus(status))
            except ValueError:
                pass
        if dept_id:
            filters.append(UserModel.department_id == dept_id)
        if filters:
            q = q.where(and_(*filters))
        q = q.order_by(UserModel.full_name)
        result = await db.execute(q)
        users = result.scalars().all()

    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "phone_number": u.phone_number,
            "telegram_id": u.telegram_id,
            "department_id": u.department_id,
            "department": u.department.name if u.department else None,
            "role": u.role.value,
            "status": u.status.value,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


class AddUserBody(BaseModel):
    telegram_id: int
    full_name: str
    phone_number: Optional[str] = None
    department_id: Optional[int] = None


@router.post("/users", status_code=201)
async def add_user(body: AddUserBody, admin: User = Depends(get_admin_user)):
    async with AsyncSessionLocal() as db:
        existing = await get_user_by_telegram_id(db, body.telegram_id)
        if existing:
            raise HTTPException(status_code=409, detail="Bu Telegram ID allaqachon mavjud")
        user = await create_user(
            db, body.telegram_id, body.full_name, body.phone_number, body.department_id
        )
        user = await update_user_status(db, user.id, UserStatus.approved)
    return {"ok": True, "id": user.id}


class UpdateUserBody(BaseModel):
    department_id: Optional[int] = None
    role: Optional[str] = None
    status: Optional[str] = None


@router.patch("/users/{user_id}")
async def update_user(user_id: int, body: UpdateUserBody, admin: User = Depends(get_admin_user)):
    async with AsyncSessionLocal() as db:
        user = await get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Topilmadi")
        if body.department_id is not None:
            user.department_id = body.department_id
        if body.status:
            user.status = UserStatus(body.status)
        if body.role:
            user.role = UserRole(body.role)
        await db.commit()
    return {"ok": True}


@router.delete("/users/{user_id}")
async def remove_user(user_id: int, admin: User = Depends(get_admin_user)):
    async with AsyncSessionLocal() as db:
        user = await update_user_status(db, user_id, UserStatus.rejected)
    if not user:
        raise HTTPException(status_code=404, detail="Topilmadi")
    return {"ok": True}


# ===========================================================================
# 5.3 Bo'limlar
# ===========================================================================

@router.get("/departments")
async def admin_get_departments(admin: User = Depends(get_admin_user)):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from db.models import Department

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Department)
            .options(selectinload(Department.head))
            .order_by(Department.name)
        )
        depts = result.scalars().all()

        return [
            {
                "id": d.id,
                "name": d.name,
                "head_user_id": d.head_user_id,
                "head_full_name": d.head.full_name if d.head else None,
            }
            for d in depts
        ]


class DeptBody(BaseModel):
    name: str


@router.post("/departments", status_code=201)
async def admin_add_department(body: DeptBody, admin: User = Depends(get_admin_user)):
    async with AsyncSessionLocal() as db:
        dept = await create_department(db, body.name.strip())
    return {"ok": True, "id": dept.id}


@router.patch("/departments/{dept_id}")
async def admin_edit_department(dept_id: int, body: DeptBody, admin: User = Depends(get_admin_user)):
    async with AsyncSessionLocal() as db:
        dept = await get_department_by_id(db, dept_id)
        if not dept:
            raise HTTPException(status_code=404, detail="Topilmadi")
        dept.name = body.name.strip()
        await db.commit()
    return {"ok": True}


@router.delete("/departments/{dept_id}")
async def admin_delete_department(dept_id: int, admin: User = Depends(get_admin_user)):
    async with AsyncSessionLocal() as db:
        ok = await delete_department(db, dept_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Topilmadi")
    return {"ok": True}


class SetHeadBody(BaseModel):
    user_id: Optional[int] = None  # None = rahbarni bekor qilish


@router.post("/departments/{dept_id}/set-head")
async def admin_set_head(dept_id: int, body: SetHeadBody, admin: User = Depends(get_admin_user)):
    async with AsyncSessionLocal() as db:
        dept = await set_department_head(db, dept_id, body.user_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Topilmadi")
    return {"ok": True}


@router.get("/departments/{dept_id}/members")
async def admin_dept_members(dept_id: int, admin: User = Depends(get_admin_user)):
    async with AsyncSessionLocal() as db:
        members = await get_department_members(db, dept_id)
    return [{"id": m.id, "full_name": m.full_name, "role": m.role.value} for m in members]


# ===========================================================================
# 5.4 Kunlik hisobot
# ===========================================================================

@router.get("/report")
async def admin_report(
    report_date: Optional[date] = Query(None),
    force: bool = Query(False, description="Test uchun vaqt tekshiruvini o'tkazib yuborish"),
    admin: User = Depends(get_admin_user),
):
    from collections import defaultdict

    target = report_date or tomorrow_tashkent()
    is_today_report = (report_date is None)

    if is_today_report and not force and not is_report_ready():
        raise HTTPException(
            status_code=425,
            detail="Kunlik hisobot 13:59 dan keyin tayyor bo'ladi.",
        )

    async with AsyncSessionLocal() as db:
        orders = await get_orders_by_date(db, target)

    lunch_by_dept  = defaultdict(list)
    dinner_by_dept = defaultdict(list)

    for o in orders:
        dept = o.user.department.name if o.user.department else "Bo'limsiz"
        row = {"user_id": o.user_id, "full_name": o.user.full_name, "is_taken": o.is_taken}
        if o.meal_type == MealType.tushlik:
            lunch_by_dept[dept].append(row)
        else:
            dinner_by_dept[dept].append(row)

    def make_sections(by_dept):
        return [
            {"department": d, "count": len(rows), "members": rows}
            for d, rows in sorted(by_dept.items())
        ]

    return {
        "report_date": str(target),
        "is_final": force or is_report_ready(),
        "lunch_total": sum(len(v) for v in lunch_by_dept.values()),
        "dinner_total": sum(len(v) for v in dinner_by_dept.values()),
        "lunch": make_sections(lunch_by_dept),
        "dinner": make_sections(dinner_by_dept),
    }


# ===========================================================================
# 5.5 Ovqat tarqatish
# ===========================================================================

@router.get("/distribution")
async def admin_distribution(
    dept_id: Optional[int] = Query(None),
    admin: User = Depends(get_admin_user),
):
    target = today_tashkent()

    async with AsyncSessionLocal() as db:
        orders = await get_orders_by_date(db, target)

    result = []
    for o in orders:
        if dept_id and o.user.department_id != dept_id:
            continue
        result.append({
            "order_id": o.id,
            "user_id": o.user_id,
            "full_name": o.user.full_name,
            "department": o.user.department.name if o.user.department else "—",
            "department_id": o.user.department_id,
            "meal_type": o.meal_type.value,
            "is_taken": o.is_taken,
            "taken_at": o.taken_at.strftime("%H:%M") if o.taken_at else None,
        })

    return result


@router.post("/distribution/{order_id}/taken")
async def admin_mark_taken(order_id: int, admin: User = Depends(get_admin_user)):
    async with AsyncSessionLocal() as db:
        order = await mark_order_taken(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Topilmadi")
    return {"ok": True}
