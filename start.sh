#!/bin/bash
# Zor Jamoa Ovqat Bot - ishga tushirish skripti (Linux/Mac)

echo "=== Zor Jamoa Ovqat Bot ==="

# Virtual environment aktivlashtirish (mavjud bo'lsa)
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Migratsiyalarni qo'llash
echo "[1/3] Migratsiyalar bajarilmoqda..."
alembic upgrade head

# API va Botni parallel ishga tushirish
echo "[2/3] API ishga tushirilmoqda (port 8000)..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

echo "[3/3] Bot ishga tushirilmoqda..."
python -m bot.main &
BOT_PID=$!

echo ""
echo "API PID: $API_PID"
echo "Bot PID: $BOT_PID"
echo ""
echo "To'xtatish uchun: Ctrl+C"

# Ikkalasini ham to'xtatish
trap "kill $API_PID $BOT_PID 2>/dev/null; exit" INT TERM
wait
