"""
DB bilan ishlash uchun asosiy CRUD funksiyalar.
Bot handlerlari va API routerlari shu funksiyalarni ishlatadi.
"""
from datetime import date
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Department, MealType, Order, User, UserRole, UserStatus


# ===========================================================================
# USER
# ===========================================================================

async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> Optional[User]:
    result = await db.execute(
        select(User)
        .where(User.telegram_id == telegram_id)
        .options(selectinload(User.department))
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.department))
    )
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    telegram_id: int,
    full_name: str,
    phone_number: Optional[str] = None,
    department_id: Optional[int] = None,
) -> User:
    user = User(
        telegram_id=telegram_id,
        full_name=full_name,
        phone_number=phone_number,
        department_id=department_id,
        role=UserRole.employee,
        status=UserStatus.pending,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_status(
    db: AsyncSession, user_id: int, status: UserStatus
) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    user.status = status
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_role(
    db: AsyncSession, user_id: int, role: UserRole
) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user


async def get_pending_users(db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(User)
        .where(User.status == UserStatus.pending)
        .options(selectinload(User.department))
        .order_by(User.created_at)
    )
    return list(result.scalars().all())


async def get_approved_users(db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(User)
        .where(User.status == UserStatus.approved)
        .options(selectinload(User.department))
    )
    return list(result.scalars().all())


async def get_department_members(db: AsyncSession, department_id: int) -> list[User]:
    result = await db.execute(
        select(User)
        .where(
            and_(
                User.department_id == department_id,
                User.status == UserStatus.approved,
            )
        )
        .order_by(User.full_name)
    )
    return list(result.scalars().all())


# ===========================================================================
# DEPARTMENT
# ===========================================================================

async def get_all_departments(db: AsyncSession) -> list[Department]:
    result = await db.execute(
        select(Department).order_by(Department.name)
    )
    return list(result.scalars().all())


async def get_department_by_id(db: AsyncSession, dept_id: int) -> Optional[Department]:
    result = await db.execute(
        select(Department).where(Department.id == dept_id)
    )
    return result.scalar_one_or_none()


async def create_department(db: AsyncSession, name: str) -> Department:
    dept = Department(name=name)
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


async def set_department_head(
    db: AsyncSession, dept_id: int, user_id: Optional[int]
) -> Optional[Department]:
    dept = await get_department_by_id(db, dept_id)
    if not dept:
        return None
    dept.head_user_id = user_id
    # Agar user_id berilsa — rolini dept_head qilamiz
    if user_id:
        await update_user_role(db, user_id, UserRole.dept_head)
    await db.commit()
    await db.refresh(dept)
    return dept


async def delete_department(db: AsyncSession, dept_id: int) -> bool:
    dept = await get_department_by_id(db, dept_id)
    if not dept:
        return False
    await db.delete(dept)
    await db.commit()
    return True


# ===========================================================================
# ORDER
# ===========================================================================

async def get_order(
    db: AsyncSession, user_id: int, order_date: date, meal_type: MealType
) -> Optional[Order]:
    result = await db.execute(
        select(Order).where(
            and_(
                Order.user_id == user_id,
                Order.order_date == order_date,
                Order.meal_type == meal_type,
            )
        )
    )
    return result.scalar_one_or_none()


async def create_order(
    db: AsyncSession,
    user_id: int,
    ordered_by_user_id: int,
    order_date: date,
    meal_type: MealType,
) -> Order:
    order = Order(
        user_id=user_id,
        ordered_by_user_id=ordered_by_user_id,
        order_date=order_date,
        meal_type=meal_type,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def get_orders_by_date(db: AsyncSession, order_date: date) -> list[Order]:
    result = await db.execute(
        select(Order)
        .where(Order.order_date == order_date)
        .options(
            selectinload(Order.user).selectinload(User.department),
            selectinload(Order.ordered_by),
        )
        .order_by(Order.meal_type, Order.created_at)
    )
    return list(result.scalars().all())


async def get_user_orders_by_date(
    db: AsyncSession, user_id: int, order_date: date
) -> list[Order]:
    result = await db.execute(
        select(Order).where(
            and_(Order.user_id == user_id, Order.order_date == order_date)
        )
    )
    return list(result.scalars().all())


async def mark_order_taken(db: AsyncSession, order_id: int) -> Optional[Order]:
    from datetime import datetime
    import pytz

    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        return None
    order.is_taken = True
    order.taken_at = datetime.now(pytz.timezone("Asia/Tashkent"))
    await db.commit()
    await db.refresh(order)
    return order


async def get_users_without_orders(db: AsyncSession, order_date: date) -> list[User]:
    """Hali buyurtma bermagan tasdiqlangan hodimlar ro'yxati (eslatma uchun)."""
    # Buyurtma bergan user_id lar
    orders_subq = (
        select(Order.user_id)
        .where(Order.order_date == order_date)
        .distinct()
        .scalar_subquery()
    )
    result = await db.execute(
        select(User).where(
            and_(
                User.status == UserStatus.approved,
                User.telegram_id.isnot(None),
                User.id.not_in(orders_subq),
            )
        )
    )
    return list(result.scalars().all())
