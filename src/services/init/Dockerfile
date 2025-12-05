FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry==2.2.1

# Copy dependency files
COPY pyproject.toml poetry.lock* README.md ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root -E langchain

# Copy init service code
COPY src/services/init/ ./src/services/init/
# Copy router app code needed for Database and Settings
COPY src/services/router/app/ ./src/services/router/app/

# Install the package itself
RUN poetry install --no-interaction --no-ansi -E langchain

# Set default command (can be overridden in docker-compose)
CMD ["python", "-m", "src.services.init.main"]

