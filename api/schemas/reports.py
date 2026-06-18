from datetime import date
from typing import Optional
from pydantic import BaseModel

from db.models import MealType


class ReportUserRow(BaseModel):
    user_id: int
    full_name: str
    is_taken: bool
    taken_at: Optional[str]


class ReportDeptSection(BaseModel):
    department_name: str
    count: int
    members: list[ReportUserRow]


class DailyReportOut(BaseModel):
    report_date: date
    is_final: bool           # 13:59 dan keyin True
    lunch_total: int
    dinner_total: int
    lunch_by_dept: list[ReportDeptSection]
    dinner_by_dept: list[ReportDeptSection]


class DistributionUserRow(BaseModel):
    order_id: int
    user_id: int
    full_name: str
    meal_type: MealType
    is_taken: bool
    taken_at: Optional[str]
