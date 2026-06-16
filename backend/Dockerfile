FROM python:3.14.6-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_CACHE_DIR=/tmp/.uv-cache

WORKDIR /app

RUN apt-get update && apt install -y --no-install-recommends \
    wget \
    gnupg2 \
    libjemalloc2 \
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

ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2

RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    appuser

RUN mkdir -p /app/media_files /app/logs && \
    chown -R appuser:appuser /app/media_files && \
    touch app.log

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-cache

COPY . .

RUN SECRET_KEY="alskjdlaskjdni;ac;mimq;schasbgyanlucdch" \
    uv run --no-dev manage.py collectstatic --no-input

RUN chown -R appuser:appuser /tmp/.uv-cache /app/logs/app.log

USER appuser

EXPOSE 8000

CMD uv run --no-dev manage.py runbolt \
    --processes $( nproc ) \
    --keep-alive 10 \
    --backlog 3000
