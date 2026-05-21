# syntax=docker/dockerfile:1

FROM python:3.14.5-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

ENV UV_CACHE_DIR=/tmp/.uv-cache

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg2 \
    lsb-release \
    ca-certificates && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/pgdg-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/pgdg-archive-keyring.gpg] http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
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

RUN mkdir -p /app/media_files /app/static_files /app/.venv /tmp/.uv-cache && \
    chown -R appuser:appuser /app/media_files /app/static_files /app/.venv /tmp/.uv-cache

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-cache

USER appuser

COPY . .

RUN SECRET_KEY="alskjdlaskjdni;ac;mimq;schasbgyanlucdch" \
    uv run --no-dev manage.py collectstatic --no-input

USER root

RUN chown -R root:root /app/static_files /app/.venv

USER appuser

EXPOSE 8000

CMD uv run --no-dev manage.py runbolt --processes $(( $(nproc) - 1 )) --keep-alive 10
