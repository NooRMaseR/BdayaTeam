# instructions for Backend

```bash
bunx wscat -c wss://localhost/ws/edit-member/Python/ -n -H "Cookie: access_token="
```

## Postgresql

to install postgresql run these commands in your terminal in order

```bash
sudo apt install postgresql
```

then start `postgresql` server

```bash
sudo service postgresql start
```

then start the `postgresql` session

```bash
sudo -u postgres psql
```

now execute the following `sql` commands with your own data

```postgresql
<!-- 1. Create the Database -->
CREATE DATABASE teambdayadb;

<!-- 2. Create a user with passwor -->
CREATE USER root WITH PASSWORD 'root123';

<!-- 3. edit the user roles -->
ALTER ROLE root SET client_encoding TO 'utf8';
ALTER ROLE root SET default_transaction_isolation TO 'read committed';
ALTER ROLE root SET timezone TO 'Africa/Cairo';

<!-- 4. add the user permissions -->
GRANT ALL PRIVILEGES ON DATABASE teambdayadb TO root;

<!-- 5. add the user permissions for public schema -->
\c teambdayadb
GRANT ALL PRIVILEGES ON SCHEMA public TO root;

<!-- that's all, now exist -->
\q
```

now you can start the `postgresql` like this

```bash
sudo systemctl enable postgresql # only if you want it to start automaticlly after booting
sudo systemctl start postgresql
```

then in your `settings.py` database add the following

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT"),
        'OPTIONS': {
            "pool": {
                "min_size": 2,
                "max_size": 10,
                "timeout": 30
            }
        }
    }
}
```

then in your `env` add these

```ini
SECRET_KEY=<djang-secret>
DB_NAME=teambdayadb
DB_HOST=localhost
DB_PORT=''
DB_USER=root
DB_PASSWORD=root123
EMAIL_HOST=<host>
EMAIL_PORT=<port>
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<app-password>
```

## uv

in the `CMD` run this command

Windows

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### install the requirements

run

```bash
uv sync --locked
```

### migrations to database

create the migrations

```bash
uv run manage.py makemigrations
```

then apply the migrations

```bash
uv run manage.py migrate
```

### creating an admin user

to create an admin user run this command

```bash
uv run manage.py createsuperuser
```

### Running the Server

run the server by using this command

```bash
uv run gunicorn \
        --workers 5 \
        --worker-connections 600 \
        --timeout 30 \
        --keep-alive 2 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind unix:/run/gunicorn.sock \
        BdayaTeam.asgi:application
```

**`--worker`** how many wokrers would you need

**`--worker-connections`** how many coonections to accept for each worker

to open `swagger-UI` open this url `http://127.0.0.1:8000/api/schema/swagger-ui/`

to open the `admin panel` open this url `http://127.0.0.1:8000/api/admin/`

## Redis

to install redis on your linux run this command

```bash
sudo apt install redis-server
```

after installation run

```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

then test it from this command

```bash
redis-cli ping # you should get PONG
```

add this line so the server don't crush when having low memory

```bash
echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf
```

## Huey

to start Huey broker in another terminal **(after initializing `gunicorn`)** run

```bash
uv run manage.py run_huey
```

**Important Note!**

so you don't start manully every time we start the machine, it's recommended to create a `systemd` for it like this

```bash
sudo nano /etc/systemd/system/huey-worker.service
```

then add these configurations

```ini
[Unit]
Description=huey Worker
After=network.target redis-server.service gunicorn.service

[Service]
User=kali
Group=kali
WorkingDirectory=/home/kali/BdayaTeam/backend
ExecStart=/home/kali/.local/bin/uv run manage.py run_huey
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

then run these commands

```bash
sudo systemctl daemon-reload
sudo systemctl enable huey-worker
sudo systemctl start huey-worker
```

## Nginx

to install `nginx` in your terminal run

```bash
sudo apt install nginx
```

now we need to bind gunicorn and nginx to comunicate using sockets for a better performance like the following

first create a systemd file called `gunicorn.socket`

```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

then add the following

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

then create a `gunicorn.service`

```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=kali
Group=www-data
WorkingDirectory=/home/kali/BdayaTeam/backend/
ExecStart=/home/kali/BdayaTeam/backend/.venv/bin/gunicorn \
        --workers 5 \
        --worker-connections 600 \
        --timeout 30 \
        --keep-alive 2 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind unix:/run/gunicorn.sock \
        BdayaTeam.asgi:application

[Install]
WantedBy=multi-user.target
```

then start the `systemctl`

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn # only if you want it to start automaticlly after booting
```

you can check the status after that

```bash
sudo systemctl status gunicorn
```

then create a symlink file for `nginx_teamDdaya.conf` in this location like this

```bash
sudo ln -s /home/kali/BdayaTeam/nginx_teamBdaya.conf /etc/nginx/sites-enabled/nginx_teamBdaya.conf
```

this will be our proxy to serve the backend and the frontend

now open `nginx.conf`

```bash
sudo nano /etc/nginx/nginx.conf
```

add these

```conf
worker_rlimit_nofile 5000; # Add this line at the top level

events {
    worker_connections 1500; # Increase this
}
```

then always test nginx when changing the configirations inside `sites-avilable` using this command

```bash
sudo nginx -t
```

you should get somthing like this

```bash
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

then restart nginx

```bash
sudo nginx -s reload
```

### Issue

you can check the permissions using this command

```bash
sudo -u www-data head -n 5 /home/kali/BdayaTeam/nginx_teamBdaya.conf
```

if `nginx` couldn't access the media of static files then you need to add the permissions to it, install `acl`

```bash
sudo apt-get install acl
```

give the permissions like these **add your own folder path**

```bash
setfacl -m u:www-data:x /home/kali/
setfacl -m u:www-data:x /home/kali/BdayaTeam/
setfacl -m u:www-data:x /home/kali/BdayaTeam/nginx_teamBdaya.conf
setfacl -m u:www-data:x /home/kali/BdayaTeam/backend/
setfacl -m u:www-data:x /home/kali/BdayaTeam/backend/static_files/
setfacl -m u:www-data:x /home/kali/BdayaTeam/backend/media_files/
setfacl -R -m u:www-data:rX /home/kali/BdayaTeam/nginx_teamBdaya.conf
setfacl -R -m u:www-data:rX /home/kali/BdayaTeam/backend/static_files
setfacl -R -m u:www-data:rX /home/kali/BdayaTeam/backend/media_files
```

that's it

## Formulas

### Gunicorn

`workers = (2 x CPU Cores) + 1`

first we need to get the how many avilable cores, in the terminal run

```bash
nproc
```

for example we get `2`, then we should have `(2 x 2) + 1 = 5 workers`

in the end the gunicorn configs should be like this

```bash
uv run gunicorn BdayaTeam.wsgi:application --workers 5 --max-requests 1000 --max-requests-jitter 50
```

### Database

`total connections = workers x max_size`

let's say we have a pool with `max_size=20`, in your database run

```bash
sudo -u postgres psql
SHOW max_connections;
```

you may get `100` connections, so we should get `5 x 20 = 100 total connections` and this is equal to `max_connections` witch is bad, we need like from 20% => 30% avilable space

if we set the `max_size=10` then we get `5 x 10 = 50` witch we get like 50% avilable space for migratios or external database operations, usually a connections takes like 2 or 3 connection

if you need more connections note that each connection depends on your `RAM`, each connection takes from `10MB -> 15MB`

to edit, run this command to get the `conf` file location

```bash
sudo -u postgres psql -c "SHOW config_file";
```

you will get the location, add edit these lines based on your need

```conf
max_connections 200;
shared_buffer 1GB
```

also you need to change how many connections for the system to open files like this

```bash
sudo nano /etc/security/limits.conf
```

add these line at the bottom

```ini
* soft nofile 5000
* hard nofile 5000
```

## **Enjoy**
