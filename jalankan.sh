#!/bin/bash

# Aktifkan virtual environment
source venv/bin/activate

# Looping sistem agar bot hidup kembali kalau ter-kill
while true; do
    echo "Mulai menjalankan bot OSINT..."
    python memek.py
    echo "⚠️ Peringatan: Bot mati atau ter-kill oleh server!"
    echo "Merestart otomatis dalam 3 detik..."
    sleep 3
done
