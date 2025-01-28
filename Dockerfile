# Use official Python 3.12 base image
FROM python:3.12.7-slim

ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry==1.8.3

# Copy only the dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN  poetry config virtualenvs.create false && poetry install --no-root

COPY . .

# Expose the FastAPI default port
EXPOSE 8000
