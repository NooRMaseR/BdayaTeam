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

## creating an admin user

to create an admin user run this command

```bash
uv run manage.py createsuperuser
```

## Running the Server

run the server by using this command

```bash
uv run gunicorn BdayaTeam.wsgi:application --workers=4
```

to open `swagger-UI` open this url `http://127.0.0.1:8000/api/schema/swagger-ui/`

to open the `admin panel` open this url `http://127.0.0.1:8000/admin/`

Enjoy
