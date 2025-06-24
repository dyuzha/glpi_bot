#!/bin/bash
set -e

# Установка кастомных сертификатов
CERTS_DIR="/data/certs"
if [ -d "$CERTS_DIR" ]; then
    echo "Найдены пользовательские сертификаты, добавляю..."
    cp "$CERTS_DIR"/* /usr/local/share/ca-certificates/ 2>/dev/null || true
    update-ca-certificates
fi


# Запуск приложения
exec python main.py
