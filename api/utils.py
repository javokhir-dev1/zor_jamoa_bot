from datetime import date, datetime, time, timedelta

import pytz

TZ = pytz.timezone("Asia/Tashkent")

CUTOFF_TIME   = time(13, 55)   # Buyurtma yopiladi
FINAL_TIME    = time(13, 59)   # Hisobot tayyor bo'ladi
DIST_END_TIME = time(20, 0)    # Tarqatish yakunlanadi


def now_tashkent() -> datetime:
    return datetime.now(TZ)


def today_tashkent() -> date:
    return now_tashkent().date()


def tomorrow_tashkent() -> date:
    return today_tashkent() + timedelta(days=1)


def is_order_open() -> bool:
    """Buyurtma qabul qilish ochiqmi? (00:00 – 13:55)"""
    return now_tashkent().time() < CUTOFF_TIME


def is_report_ready() -> bool:
    """Kunlik hisobot tayyor bo'ldimi? (13:59 dan keyin)"""
    return now_tashkent().time() >= FINAL_TIME


def order_target_date() -> date:
    """Buyurtma qaysi kun uchun — ertangi sana."""
    return tomorrow_tashkent()
