#!/bin/bash

# Удаляем контейнер
docker rm gbc 2>/dev/null

# Удаляем образ
docker rmi glpi_bot 2>/dev/null

echo "Очистка завершена"
