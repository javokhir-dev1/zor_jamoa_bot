import enum
from datetime import datetime, date

from sqlalchemy import (
    BigInteger, Boolean, Date, DateTime, Enum, ForeignKey,
    Integer, String, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


# ---------------------------------------------------------------------------
# Enumlar
# ---------------------------------------------------------------------------

class UserRole(str, enum.Enum):
    employee  = "employee"    # Oddiy hodim
    dept_head = "dept_head"   # Bo'lim rahbari
    admin     = "admin"       # Admin/moderator


class UserStatus(str, enum.Enum):
    pending  = "pending"   # Ariza yuborilgan, tasdiqlanmagan
    approved = "approved"  # Tasdiqlangan
    rejected = "rejected"  # Rad etilgan


class MealType(str, enum.Enum):
    tushlik      = "tushlik"       # Обед
    kechki_ovqat = "kechki_ovqat"  # Ужин


# ---------------------------------------------------------------------------
# departments
# ---------------------------------------------------------------------------

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Bo'lim rahbari (users.id ga FK, circular ref uchun string)
    head_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", use_alter=True, name="fk_dept_head"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    head: Mapped["User | None"] = relationship(
        "User", foreign_keys=[head_user_id], back_populates="headed_department"
    )
    members: Mapped[list["User"]] = relationship(
        "User", foreign_keys="User.department_id", back_populates="department"
    )

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name!r}>"


# ---------------------------------------------------------------------------
# users
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

    department_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=True
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.employee, nullable=False
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), default=UserStatus.pending, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    department: Mapped["Department | None"] = relationship(
        "Department", foreign_keys=[department_id], back_populates="members"
    )
    headed_department: Mapped["Department | None"] = relationship(
        "Department", foreign_keys="Department.head_user_id", back_populates="head"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", foreign_keys="Order.user_id", back_populates="user"
    )
    placed_orders: Mapped[list["Order"]] = relationship(
        "Order", foreign_keys="Order.ordered_by_user_id", back_populates="ordered_by"
    )

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.admin

    @property
    def is_dept_head(self) -> bool:
        return self.role == UserRole.dept_head

    @property
    def is_approved(self) -> bool:
        return self.status == UserStatus.approved

    def __repr__(self) -> str:
        return f"<User id={self.id} tg={self.telegram_id} name={self.full_name!r}>"


# ---------------------------------------------------------------------------
# orders
# ---------------------------------------------------------------------------

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Buyurtma kimga tegishli
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    # Buyurtmani kim berdi (o'zi yoki bo'lim rahbari)
    ordered_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    order_date: Mapped[date] = mapped_column(Date, nullable=False)  # Ertangi sana
    meal_type: Mapped[MealType] = mapped_column(Enum(MealType), nullable=False)

    # Tarqatish nazorati
    is_taken: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    taken_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Unique: bir hodim bir kunga bir xil ovqat turidan faqat 1 ta buyurtma
    __table_args__ = (
        UniqueConstraint("user_id", "order_date", "meal_type", name="uq_user_date_meal"),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="orders"
    )
    ordered_by: Mapped["User"] = relationship(
        "User", foreign_keys=[ordered_by_user_id], back_populates="placed_orders"
    )

    def __repr__(self) -> str:
        return (
            f"<Order id={self.id} user_id={self.user_id} "
            f"date={self.order_date} meal={self.meal_type}>"
        )
