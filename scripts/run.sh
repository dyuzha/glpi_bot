#!/bin/bash

# Проверяем существование образа
if ! docker image inspect myapp >/dev/null 2>&1; then
  echo "Образ 'myapp' не найден. Сначала выполните ./build.sh"
  exit 1
fi

# if [ ! -f ../.env ]; then
#   echo "Файл .env не найден. Скопируйте .env.example и настройте"
#   exit 1
# fi


# Запускаем контейнер в интерактивном режиме с пробросом портов (если нужно)
docker run -it --rm \
    \ -p 8080:8080 \
    # \ -v $(pwd)/logs:/app/logs \  # Монтируем папку с логами
    \ --env-file .env \  # Подгружаем переменные окружения
    \ --name gbc glpi_bot

# Для фонового режима замените `-it` на `-d`
