from fastapi import APIRouter, Depends

from api.auth import get_current_user
from api.schemas.departments import DepartmentMemberOut, DepartmentOut
from api.utils import order_target_date
from db.crud import get_all_departments, get_department_members, get_order
from db.database import AsyncSessionLocal
from db.models import MealType, User, UserRole

router = APIRouter()


@router.get("/", response_model=list[DepartmentOut])
async def list_departments(current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as db:
        depts = await get_all_departments(db)

    return [
        DepartmentOut(
            id=d.id,
            name=d.name,
            head_user_id=d.head_user_id,
            head_full_name=d.head.full_name if d.head else None,
        )
        for d in depts
    ]


@router.get("/my-dept/members", response_model=list[DepartmentMemberOut])
async def my_dept_members(current_user: User = Depends(get_current_user)):
    """
    Bo'lim rahbari uchun: o'z bo'limidagi hodimlar va ularning
    ertangi kun uchun buyurtma holati (qizil/yashil).
    """
    if current_user.role not in (UserRole.dept_head, UserRole.admin):
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q.")

    dept_id = current_user.department_id
    if not dept_id:
        return []

    target = order_target_date()

    async with AsyncSessionLocal() as db:
        members = await get_department_members(db, dept_id)
        result = []
        for member in members:
            lunch  = await get_order(db, member.id, target, MealType.tushlik)
            dinner = await get_order(db, member.id, target, MealType.kechki_ovqat)
            result.append(DepartmentMemberOut(
                id=member.id,
                full_name=member.full_name,
                has_lunch=lunch is not None,
                has_dinner=dinner is not None,
            ))

    return result
