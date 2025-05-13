#!/bin/bash

# Удаляем только контейнер (без удаления образа)
docker rm -f gbc 2>/dev/null
echo "Контейнер gbc удалён"
