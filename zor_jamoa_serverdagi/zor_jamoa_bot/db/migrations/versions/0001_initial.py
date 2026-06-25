"""Initial schema: departments, users, orders

Revision ID: 0001
Revises:
Create Date: 2026-06-18
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- departments (head_user_id keyinroq qo'shiladi — circular FK) ---
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("head_user_id", sa.Integer(), nullable=True),  # FK keyinroq
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("department_id", sa.Integer(), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column(
            "role",
            sa.Enum("employee", "dept_head", "admin", name="userrole"),
            nullable=False,
            server_default="employee",
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "approved", "rejected", name="userstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    # --- departments.head_user_id FK (circular) ---
    op.create_foreign_key(
        "fk_dept_head",
        "departments", "users",
        ["head_user_id"], ["id"],
    )

    # --- orders ---
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("ordered_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column(
            "meal_type",
            sa.Enum("tushlik", "kechki_ovqat", name="mealtype"),
            nullable=False,
        ),
        sa.Column("is_taken", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "order_date", "meal_type", name="uq_user_date_meal"),
    )
    op.create_index("ix_orders_order_date", "orders", ["order_date"])
    op.create_index("ix_orders_user_id", "orders", ["user_id"])


def downgrade() -> None:
    op.drop_table("orders")
    op.drop_constraint("fk_dept_head", "departments", type_="foreignkey")
    op.drop_table("users")
    op.drop_table("departments")

    # Enum turlarini tozalash (PostgreSQL)
    op.execute("DROP TYPE IF EXISTS mealtype")
    op.execute("DROP TYPE IF EXISTS userstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
