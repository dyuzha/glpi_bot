#!/bin/bash

# Удаляем контейнер
docker rm -f gbc 2>/dev/null

# Удаляем образ
docker rmi glpi_bot 2>/dev/null

echo "Полная очистка завершена"

