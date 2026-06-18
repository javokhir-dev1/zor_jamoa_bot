from typing import Optional
from pydantic import BaseModel


class DepartmentOut(BaseModel):
    id: int
    name: str
    head_user_id: Optional[int]
    head_full_name: Optional[str]

    model_config = {"from_attributes": True}


class DepartmentMemberOut(BaseModel):
    id: int
    full_name: str
    has_lunch: bool    # bugungi tushlik buyurtmasi bormi
    has_dinner: bool   # bugungi kechki ovqat buyurtmasi bormi

    model_config = {"from_attributes": True}
