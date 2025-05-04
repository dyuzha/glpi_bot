#!/bin/bash

# Проверяем суествование переменной с путем к файлам
if [ -z "${CONFIGS}" ]; then
    echo "Переменная CONFIGS не определена или пустая"
    exit 1
fi


# Переменные для путей
SETTINGS_PATH="$CONFIGS/settings.ini"
LOGGING_CONFIG="$CONFIGS/logging_config.json"

#Проверка существования файлов
if [ ! -f "$SETTINGS_PATH" ]; then
  echo "Файл $SETTINGS_PATH не найден."
  exit 1
fi
if [ ! -f "$LOGGING_CONFIG" ]; then
  echo "Файл $LOGGING_CONFIG не найден."
  exit 1
fi


# Проверяем существование образа
if ! docker image inspect glpi_bot >/dev/null 2>&1; then
  echo "Образ 'glpi_bot' не найден. Сначала выполните ./build.sh"
  exit 1
fi


# Запуск контейнера
docker run -d \
  -v "${SETTINGS_PATH}:/glpi_bot/settings.ini" \
  -e GLPI_TG_SETTINGS_CONF="/glpi_bot/settings.ini" \
  -v "${LOGGING_CONFIG}:/glpi_bot/logging_config.json" \
  -e GLPI_TG_LOG_CONF="/glpi_bot/logging_config.json" \
  --name gbc \
  glpi_bot
# Для интерактивного режима замените `-d` на `-it`
