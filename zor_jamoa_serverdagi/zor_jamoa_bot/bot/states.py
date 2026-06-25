from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_phone = State()   # Telefon raqami kutilmoqda
    waiting_name  = State()   # Ism-familiya kutilmoqda
    waiting_dept  = State()   # Bo'lim tanlash kutilmoqda


class AddUserStates(StatesGroup):
    waiting_telegram_id = State()  # Telegram ID
    waiting_full_name   = State()  # Ism-familiya
    waiting_phone       = State()  # Telefon (ixtiyoriy)
    waiting_dept        = State()  # Bo'lim tanlash


class DeptStates(StatesGroup):
    waiting_new_name    = State()  # Yangi bo'lim nomi
    waiting_edit_name   = State()  # Tahrirlash uchun yangi nom
    waiting_head_select = State()  # Rahbar tanlash
