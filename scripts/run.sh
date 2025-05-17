#!/bin/bash

# Проверяем суествование переменной с путем к файлам
if [ -z "${GLPI_TG_CONFIG_DIR}" ]; then
    echo "Переменная GLPI_TG_CONFIG_DIR не определена или пустая"
    exit 1
fi

# Переменные для путей
SETTINGS_PATH="${GLPI_TG_CONFIG_DIR}/settings.ini"
LOGGING_CONFIG="${GLPI_TG_CONFIG_DIR}/logging_config.json"
MAIL_CONFIG="${GLPI_TG_CONFIG_DIR}/mail_config.ini"

#Проверка существования файлов
if [ ! -f "$SETTINGS_PATH" ]; then
  echo "Файл $SETTINGS_PATH не найден."
  exit 1
fi

if [ ! -f "$LOGGING_CONFIG" ]; then
  echo "Файл $LOGGING_CONFIG не найден."
  exit 1
fi

if [ ! -f "$MAIL_CONFIG" ]; then
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
  -v "${GLPI_TG_CONFIG_DIR}:/configs" \
  --name gbc \
  glpi_bot

# Для интерактивного режима замените `-d` на `-it`
