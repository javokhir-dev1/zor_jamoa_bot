@echo off
REM Zor Jamoa Ovqat Bot - ishga tushirish skripti (Windows)

echo === Zor Jamoa Ovqat Bot ===

REM Virtual environment aktivlashtirish (mavjud bo'lsa)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Migratsiyalarni qo'llash
echo [1/3] Migratsiyalar bajarilmoqda...
alembic upgrade head
if %ERRORLEVEL% neq 0 (
    echo XATO: Migratsiya bajarilmadi! PostgreSQL ishlab turibdimi?
    pause
    exit /b 1
)

REM API ni alohida oynada ishga tushirish
echo [2/3] API ishga tushirilmoqda (port 8000)...
start "Zor Jamoa API" cmd /k uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

REM Botni alohida oynada ishga tushirish
echo [3/3] Bot ishga tushirilmoqda...
start "Zor Jamoa Bot" cmd /k python -m bot.main

echo.
echo Tayyor! API va Bot alohida oynalarda ishga tushdi.
echo To'xtatish uchun oynalarni yoping.
pause
