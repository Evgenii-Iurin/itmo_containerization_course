FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry==2.2.1

COPY pyproject.toml poetry.lock* README.md ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --no-root --extras langchain

COPY src/services/router/ ./src/services/router/

RUN poetry install --no-interaction --no-ansi -E langchain

EXPOSE 8000

CMD ["uvicorn", "src.services.router.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

