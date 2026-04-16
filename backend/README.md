# instructions for Backend

just run `setup.sh` from the project root and it will setup and installs the dependencies

in your `env` add these

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
VAPID_PRIVATE_KEY=VAPID_PRIVATE_KEY
VAPID_ADMIN_EMAIL=VAPID_ADMIN_EMAIL
```

## creating an admin user

to create an admin user run this command

```bash
uv run manage.py createsuperuser
```

### Running the Server

run the server by using this command

```bash
uv run gunicorn \
        --workers 4 \
        --worker-connections 600 \
        --timeout 30 \
        --keep-alive 2 \
        --worker-class uvicorn.workers.UvicornWorker \
        --forwarded-allow-ips="*" \
        --bind unix:/run/gunicorn.sock \
        BdayaTeam.asgi:application
```

**`--worker`** how many wokrers would you need

**`--worker-connections`** how many coonections to accept for each worker

to open `openApi` open this url `http://localhost:8000/api/docs`

## Redis

test it from this command

```bash
redis-cli ping # you should get PONG
```

## Nginx

open `nginx.conf`

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
