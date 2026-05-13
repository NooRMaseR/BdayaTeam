# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.14.2
FROM python:${PYTHON_VERSION}-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN mkdir -p /app /opt/venv && chown -R appuser:appuser /app /opt/venv

USER appuser

COPY . .

ENV UV_PROJECT_ENVIRONMENT=/opt/venv

COPY --chown=appuser:appuser pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-cache

COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["uv", "run", "manage.py", "runbolt", "--process", "3"]
