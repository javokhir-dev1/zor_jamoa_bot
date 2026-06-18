"""
Telegram Web App initData tekshiruvi.
Docs: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""
import hashlib
import hmac
import json
from urllib.parse import parse_qsl, unquote

from fastapi import Depends, Header, HTTPException, status

from config import settings
from db.crud import get_user_by_telegram_id, create_user
from db.database import AsyncSessionLocal
from db.models import User, UserRole, UserStatus


def _verify_init_data(init_data: str) -> dict:
    """
    initData ni tekshiradi va user dict qaytaradi.
    Noto'g'ri bo'lsa HTTPException ko'taradi.
    """
    try:
        params = dict(parse_qsl(unquote(init_data), keep_blank_values=True))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="initData parse error")

    received_hash = params.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="hash missing")

    # Data-check-string: kalitlar alfavit tartibida, \n bilan ajratilgan
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(params.items())
    )

    # HMAC-SHA256: secret_key = HMAC-SHA256("WebAppData", bot_token)
    secret_key = hmac.new(
        b"WebAppData",
        settings.BOT_TOKEN.encode(),
        hashlib.sha256,
    ).digest()

    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="initData invalid")

    # user field ni parse qilish
    user_json = params.get("user")
    if not user_json:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user missing")

    try:
        return json.loads(user_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user parse error")


async def get_current_user(
    x_init_data: str = Header(..., alias="X-Init-Data"),
) -> User:
    """
    FastAPI dependency — so'rovdan foydalanuvchini aniqlaydi.
    Header: X-Init-Data: <Telegram.WebApp.initData>
    """
    tg_user = _verify_init_data(x_init_data)
    telegram_id = tg_user.get("id")
    if not telegram_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="telegram_id missing")

    is_admin_id = telegram_id in settings.ADMIN_IDS

    async with AsyncSessionLocal() as db:
        user = await get_user_by_telegram_id(db, telegram_id)

        # ADMIN_IDS da bor, lekin bazada yo'q → avtomatik yaratamiz
        if not user and is_admin_id:
            full_name = tg_user.get("first_name", "Admin")
            last_name = tg_user.get("last_name", "")
            if last_name:
                full_name = f"{full_name} {last_name}"
            user = await create_user(db, telegram_id, full_name)
            user.status = UserStatus.approved
            user.role   = UserRole.admin
            await db.commit()
            await db.refresh(user)

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found")

    # ADMIN_IDS da bo'lsa status tekshiruvi o'tkazib yuboriladi
    if not is_admin_id and user.status != UserStatus.approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User status: {user.status.value}",
        )

    return user


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    """Faqat admin uchun dependency.
    DB role=admin YOKI .env ADMIN_IDS da bo'lsa ruxsat beriladi.
    """
    from db.models import UserRole
    is_admin = (
        user.role == UserRole.admin
        or user.telegram_id in settings.ADMIN_IDS
    )
    if not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user
