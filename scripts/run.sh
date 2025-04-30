#!/bin/bash

# Переменные для путей
SETTINGS_PATH="$CONFIGS\settings.ini"
LOGGING_CONFIG="$CONFIGS\logging_config.json"

# Проверяем существование образа
if ! docker image inspect myapp >/dev/null 2>&1; then
  echo "Образ 'myapp' не найден. Сначала выполните ./build.sh"
  exit 1
fi

# Проверка существование файлов
# ...

# if [ ! -f ../.env ]; then
#   echo "Файл .env не найден. Скопируйте .env.example и настройте"
#   exit 1
# fi


docker run -d  \
    \ -v "${SETTINGS_PATH}:/glpi_bot/settings.ini" \
    \ -e GLPI_TG_SETTINGS_CONF="/glpi_bot/settings.ini" \
    \ -v "${LOGGING_CONFIG}:/glpi_bot/logging_config.json" \
    \ -e GLPI_TG_LOG_CONF="/glpi_bot/logging_config.json"
    \ --name gbc \
    glpi_bot

# Для фонового режима замените `-it` на `-d`
#
