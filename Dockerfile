FROM python:3.9-slim

LABEL maintainer="Dyuzhev Matvey"

# Устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
ENV POETRY_VERSION=1.7.1
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"

# Копируем файлы проекта
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости проекта
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Копируем скрипты и делаем их исполняемыми
COPY ./scripts ./scripts
RUN chmod +x /app/scripts/*.sh

# Копируем остальные файлы приложения
COPY . .

# Запускаем приложение
CMD ["python", "main.py"]
