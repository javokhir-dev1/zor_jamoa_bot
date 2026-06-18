from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from db.models import MealType


class OrderCreate(BaseModel):
    meal_type: MealType
    target_user_id: Optional[int] = None  # Bo'lim rahbari boshqasi uchun bersa


class OrderOut(BaseModel):
    id: int
    user_id: int
    user_full_name: str
    department_name: Optional[str]
    meal_type: MealType
    order_date: date
    is_taken: bool
    taken_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class MyOrdersOut(BaseModel):
    order_date: date
    has_lunch: bool
    has_dinner: bool


class BulkOrderCreate(BaseModel):
    """Bo'lim rahbari — bir nechta hodimga buyurtma."""
    user_ids: list[int]
    meal_type: MealType
