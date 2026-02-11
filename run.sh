#!/bin/zsh
if [ ! -d "venv" ]; then
    echo "🚀 Sanal ortam oluşturuluyor..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "📦 Kütüphaneler kontrol ediliyor..."
pip install -r requirements.txt --quiet
echo "🤖 Finans Ajanı başlatılıyor..."
python3 main.py
