#!/bin/bash
# ===========================================
# Deploy Tradingbot to AWS
# ===========================================

set -e

echo "==========================================="
echo "Tradingbot Deployment Script"
echo "==========================================="

cd ~/Tradingbot

echo "📦 Pulling latest code..."
git stash || true
git pull origin main

echo "🔄 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt -q

echo "🔄 Restarting server..."
pkill -f "uvicorn backend.main:app" || true
sleep 2

screen -S tradingbot -X quit 2>/dev/null || true
screen -dmS tradingbot
screen -S tradingbot -X stuff "cd ~/Tradingbot && source venv/bin/activate && uvicorn backend.main:app --host 0.0.0.0 --port 8000$(printf '\r')"

sleep 3

if pgrep -f "uvicorn backend.main:app" > /dev/null; then
    echo "✅ Server started!"
else
    echo "❌ Server failed. Check: screen -r tradingbot"
fi

echo "==========================================="
