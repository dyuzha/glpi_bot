FROM python:3.9-slim

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

# Сначала копируем только файлы зависимостей
WORKDIR /glpi_bot
COPY ./app/pyproject.toml ./app/poetry.lock ./

# Устанавливаем зависимости проекта
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Копируем остальные файлы приложения
COPY . .

# Копируем скрипты и делаем их исполняемыми
COPY ./scripts ./scripts
RUN chmod +x scripts/*.sh

# Запускаем приложение
CMD ["python", "./app/main.py"]
# CMD ["python", "./app/test_mail.py"]
