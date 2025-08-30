# Базовый образ
FROM python:3.11-slim

# Устанавливаем системные зависимости и очищаем кэш
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

# Рабочая директория
WORKDIR /app

# Копируем файлы зависимостей primero (для кэширования)
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Копируем остальные файлы
COPY . .

# Создаем директории
RUN mkdir -p staticfiles media

# Порты
EXPOSE 8000

# Команда запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
