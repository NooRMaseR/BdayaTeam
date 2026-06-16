# BdayaTeam

BdayaTeam is a Team for teaching free courses in most of the technical skils, this is a website made to enhance the experiance improve the team performance

# instructions for first build

## 1- Add the ENVs

create `.env` file for (BdayaTeam, backend, frontend) with the schema of `.env.example` file in each one of them

---

if you want to change the database credentials then change it in the `.env` file inside the `backend` folder

---

for the domain name, edit the `nginx_teamBdaya_docker.conf` and edit `compose.yaml` at `nginx` service for prober volumes and go to `backend/BdayaTeam/settings.py` and edit the `ALLOWED_HOSTS` atr the top and `CORS` at the bottom

---

for the user in docker, edit the `Dockerfile` at `useradd` or `adduser` code

---

for the dev mode in `Next.js`, uncomment the `dockerfile` property in `compose.yaml`

## 2- Run docker

you need to run docker like this first

```bash
docker compose up -d
```

## 3- migrate the database

you need to make\apply migrations for the database as the root user for creating migrations files

```bash
docker compose exec -u root bolt uv run --no-dev manage.py makemigrations
docker compose exec -u root bolt uv run --no-dev manage.py migrate
```

## 4- create superuser

```bash
docker compose exec bolt uv run --no-dev manage.py createsuperuser
```

## 5- Restart the backend (bolt)

you need to restart the backend for the changes

```bash
docker compose restart bolt
```

## 6- Testing

you can enable the docs from `backend/core/api.py` to test the endpoints or you can run this command to check `Redis` and the `Database`

```bash
curl https://localhost/api/ready/ -i
```

## Enjoy
