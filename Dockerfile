FROM python:3.13-slim AS builder

LABEL maintainer="Dyuzhev Matvey"

# Устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
ENV POETRY_VERSION=2.1.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/opt/poetry/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    # Создаем символическую ссылку для глобального доступа
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Устанавливаем плагин poetry
RUN poetry self add poetry-plugin-export

WORKDIR /src/glpi_bot

# Сначала копируем только файлы зависимостей (Для кеширования)
COPY ./pyproject.toml ./poetry.lock ./

# Генерируем requirements.txt с разделением dev и prod
RUN poetry export --without-hashes --only=main --no-interaction -f requirements.txt -o requirements.txt
RUN poetry export --without-hashes --only=dev --no-interaction -f requirements.txt -o requirements-dev.txt


FROM python:3.13-slim AS production

# Установка корневых сертификатов
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Устанавливаем зависимости
COPY --from=builder /src/glpi_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы приложения
COPY ./src/glpi_bot ./glpi_bot
COPY ./src/main.py .

# Копируем дополнительные сертификаты (если есть)
# COPY ./data/certs/* /usr/local/share/ca-certificates/

COPY ./scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Создаем папку для конфигов
RUN mkdir -p /configs

# Указываем том для монтирования конфигов
VOLUME /configs

# Устанавливаем переменные окружения для конфигов
ENV GLPI_TG_LOG_CONF=/configs/logging_config.json
ENV GLPI_TG_MAIL_CONF=/configs/mail_config.ini
ENV GLPI_TG_SETTINGS=/configs/settings.ini

# Запускаем приложение
# CMD ["python", "main.py"]
CMD ["/entrypoint.sh", "main.py"]
