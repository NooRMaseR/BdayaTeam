# instructions for Backend

## Setup uv

in the `CMD` run this command

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## install the requirements
run 

```bash
uv sync --locked
```

## migrations to database

create the migrations

```bash
uv run manage.py makemigrations
```

then apply the migrations

```bash
uv run manage.py migrate
```

## Running the Server

run the server by using this command

```bash
uv run manage.py runserver
```

then head to this url to open `swagger-UI`

`http://127.0.0.1:8000/api/schema/swagger-ui/`

Enjoy
