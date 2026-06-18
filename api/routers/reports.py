from collections import defaultdict
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.auth import get_admin_user
from api.schemas.reports import (
    DailyReportOut,
    DistributionUserRow,
    ReportDeptSection,
    ReportUserRow,
)
from api.utils import is_report_ready, today_tashkent
from db.crud import get_orders_by_date, mark_order_taken
from db.database import AsyncSessionLocal
from db.models import MealType, User

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /reports/daily — kunlik hisobot
# ---------------------------------------------------------------------------

@router.get("/daily", response_model=DailyReportOut)
async def daily_report(
    report_date: date = Query(default=None),
    admin: User = Depends(get_admin_user),
):
    """
    Kunlik yakuniy hisobot.
    - Parametrsiz: bugun uchun (today) — faqat 13:59 dan keyin to'liq ko'rinadi
    - ?report_date=2026-06-19: o'tgan kunlar uchun har doim mavjud
    """
    target = report_date or today_tashkent()
    is_today = (target == today_tashkent())
    is_final = (not is_today) or is_report_ready()

    if is_today and not is_final:
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="Kunlik hisobot 13:59 dan keyin tayyor bo'ladi.",
        )

    async with AsyncSessionLocal() as db:
        orders = await get_orders_by_date(db, target)

    # Bo'lim bo'yicha guruhlash
    lunch_by_dept:  dict[str, list] = defaultdict(list)
    dinner_by_dept: dict[str, list] = defaultdict(list)

    for o in orders:
        dept_name = o.user.department.name if o.user.department else "Bo'limsiz"
        row = ReportUserRow(
            user_id=o.user_id,
            full_name=o.user.full_name,
            is_taken=o.is_taken,
            taken_at=o.taken_at.strftime("%H:%M") if o.taken_at else None,
        )
        if o.meal_type == MealType.tushlik:
            lunch_by_dept[dept_name].append(row)
        else:
            dinner_by_dept[dept_name].append(row)

    lunch_sections = [
        ReportDeptSection(department_name=d, count=len(rows), members=rows)
        for d, rows in sorted(lunch_by_dept.items())
    ]
    dinner_sections = [
        ReportDeptSection(department_name=d, count=len(rows), members=rows)
        for d, rows in sorted(dinner_by_dept.items())
    ]

    return DailyReportOut(
        report_date=target,
        is_final=is_final,
        lunch_total=sum(s.count for s in lunch_sections),
        dinner_total=sum(s.count for s in dinner_sections),
        lunch_by_dept=lunch_sections,
        dinner_by_dept=dinner_sections,
    )


# ---------------------------------------------------------------------------
# GET /reports/distribution — ovqat tarqatish (bugungi kun)
# ---------------------------------------------------------------------------

@router.get("/distribution", response_model=list[DistributionUserRow])
async def distribution_list(
    dept_id: int = Query(..., description="Bo'lim IDsi"),
    meal_type: MealType = Query(default=None),
    admin: User = Depends(get_admin_user),
):
    """
    Bugungi tarqatish ro'yxati — bitta bo'lim uchun.
    Ovqatlar ertangi kunda keladi, shuning uchun order_date = bugun.
    """
    from api.utils import today_tashkent
    target = today_tashkent()

    async with AsyncSessionLocal() as db:
        orders = await get_orders_by_date(db, target)

    rows = []
    for o in orders:
        if o.user.department_id != dept_id:
            continue
        if meal_type and o.meal_type != meal_type:
            continue
        rows.append(DistributionUserRow(
            order_id=o.id,
            user_id=o.user_id,
            full_name=o.user.full_name,
            meal_type=o.meal_type,
            is_taken=o.is_taken,
            taken_at=o.taken_at.strftime("%H:%M") if o.taken_at else None,
        ))

    return rows


# ---------------------------------------------------------------------------
# POST /reports/distribution/{order_id}/taken — "Buyurtma topshirildi"
# ---------------------------------------------------------------------------

@router.post("/distribution/{order_id}/taken")
async def mark_taken(
    order_id: int,
    admin: User = Depends(get_admin_user),
):
    async with AsyncSessionLocal() as db:
        order = await mark_order_taken(db, order_id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyurtma topilmadi.")

    return {"ok": True, "order_id": order.id, "taken_at": str(order.taken_at)}
