#!/bin/bash

# Убедимся, что Docker запущен
if ! docker info >/dev/null 2>&1; then
    echo "Docker не запущен. Запустите Docker Desktop и повторите попытку."
    exit 1
fi

# Собираем образ с тегом 'myapp'
docker build -t glpi_bot .

echo "Образ 'myapp' успешно собран"
