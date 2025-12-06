# ХОРОШИЙ Dockerfile - исправлены все плохие практики

# Хорошая практика 1: Использование конкретной версии базового образа
FROM python:3.11-slim

# Хорошая практика 2: Установка только необходимых системных пакетов
# slim образ уже минималистичен, дополнительных пакетов не требуется

# Хорошая практика 3: Установка переменных окружения до копирования файлов
# Это позволяет лучше кэшировать слои
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Хорошая практика 4: Копирование файлов зависимостей отдельно для лучшего кэширования
COPY pyproject.toml poetry.lock* README.md ./

# Хорошая практика 5: Установка poetry и зависимостей без кэширования
RUN pip install --no-cache-dir poetry==2.2.1 && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --extras langchain

# Хорошая практика 6: Копирование исходного кода после установки зависимостей
# Это позволяет переиспользовать слой с зависимостями при изменении кода
COPY src/services/router/ ./src/services/router/

# Хорошая практика 7: Установка пакета в режиме production (без dev зависимостей)
RUN poetry install --no-interaction --no-ansi -E langchain --only=main

# Хорошая практика 8: Создание непривилегированного пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app

# Хорошая практика 9: Переключение на непривилегированного пользователя
USER appuser

# Хорошая практика 10: Использование переменной окружения для порта
ENV PORT=8000

EXPOSE 8000

# Хорошая практика 11: Использование переменной окружения в CMD
CMD ["sh", "-c", "uvicorn src.services.router.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
