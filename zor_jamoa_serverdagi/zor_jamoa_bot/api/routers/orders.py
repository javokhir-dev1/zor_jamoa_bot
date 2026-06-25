from fastapi import APIRouter, Depends, HTTPException, status

from api.auth import get_current_user
from api.schemas.orders import BulkOrderCreate, MyOrdersOut, OrderCreate, OrderOut
from api.utils import is_order_open, order_target_date
from db.crud import (
    create_order,
    get_department_members,
    get_order,
    get_user_by_id,
    get_user_orders_by_date,
)
from db.database import AsyncSessionLocal
from db.models import MealType, User, UserRole

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /orders/my — mening bugungi buyurtmalarim
# ---------------------------------------------------------------------------

@router.get("/my", response_model=MyOrdersOut)
async def my_orders(current_user: User = Depends(get_current_user)):
    target = order_target_date()
    async with AsyncSessionLocal() as db:
        orders = await get_user_orders_by_date(db, current_user.id, target)

    meal_types = {o.meal_type for o in orders}
    return MyOrdersOut(
        order_date=target,
        has_lunch=MealType.tushlik in meal_types,
        has_dinner=MealType.kechki_ovqat in meal_types,
    )


# ---------------------------------------------------------------------------
# POST /orders — buyurtma berish (oddiy hodim)
# ---------------------------------------------------------------------------

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_my_order(
    body: OrderCreate,
    current_user: User = Depends(get_current_user),
):
    if not is_order_open():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ertangi kun uchun buyurtma berish yakunlandi. "
                   "Iltimos, buyurtmalaringizni har kuni 13:55 dan kechiktirmasdan yozib qoldiring.",
        )

    target = order_target_date()

    async with AsyncSessionLocal() as db:
        # Duplicate tekshiruv
        existing = await get_order(db, current_user.id, target, body.meal_type)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bu ovqat turi uchun allaqachon buyurtma berilgan.",
            )

        order = await create_order(
            db=db,
            user_id=current_user.id,
            ordered_by_user_id=current_user.id,
            order_date=target,
            meal_type=body.meal_type,
        )

        # Response uchun user va dept ma'lumotlari
        user = await get_user_by_id(db, order.user_id)

    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        user_full_name=user.full_name,
        department_name=user.department.name if user.department else None,
        meal_type=order.meal_type,
        order_date=order.order_date,
        is_taken=order.is_taken,
        taken_at=order.taken_at,
        created_at=order.created_at,
    )


# ---------------------------------------------------------------------------
# POST /orders/bulk — bo'lim rahbari bir nechta hodimga buyurtma
# ---------------------------------------------------------------------------

@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_order(
    body: BulkOrderCreate,
    current_user: User = Depends(get_current_user),
):
    # Faqat bo'lim rahbari yoki admin
    if current_user.role not in (UserRole.dept_head, UserRole.admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q.")

    if not is_order_open():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Buyurtma vaqti tugagan.",
        )

    if not body.user_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_ids bo'sh.")

    target = order_target_date()
    created, skipped = [], []

    async with AsyncSessionLocal() as db:
        # Bo'lim rahbari faqat o'z bo'limi hodimlariga buyurtma bera oladi
        if current_user.role == UserRole.dept_head and current_user.department_id:
            allowed_members = await get_department_members(db, current_user.department_id)
            allowed_ids = {m.id for m in allowed_members}
        else:
            allowed_ids = None  # admin — cheklov yo'q

        for uid in body.user_ids:
            if allowed_ids is not None and uid not in allowed_ids:
                skipped.append({"user_id": uid, "reason": "Boshqa bo'lim hodimi"})
                continue

            existing = await get_order(db, uid, target, body.meal_type)
            if existing:
                skipped.append({"user_id": uid, "reason": "Allaqachon buyurtma bor"})
                continue

            order = await create_order(
                db=db,
                user_id=uid,
                ordered_by_user_id=current_user.id,
                order_date=target,
                meal_type=body.meal_type,
            )
            created.append(order.id)

    return {
        "created_count": len(created),
        "skipped_count": len(skipped),
        "skipped": skipped,
    }
