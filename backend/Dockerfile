# syntax=docker/dockerfile:1

FROM python:3.14.5-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

ENV UV_CACHE_DIR=/tmp/.uv-cache

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends wget gnupg2 lsb-release ca-certificates

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/pgdg-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/pgdg-archive-keyring.gpg] http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client-18 \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    appuser

RUN mkdir -p /tmp/.uv-cache && \
    chown -R appuser:appuser /app /tmp/.uv-cache

RUN mkdir -p /app/static_files /app/media_files && \
    chown -R appuser:appuser /app/static_files /app/media_files

USER appuser

COPY --chown=appuser:appuser pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-cache

COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD uv run --no-dev manage.py runbolt --processes $(( $(nproc) - 1 )) --keep-alive 10
