# instructions for Backend

## creating an admin user

to create an admin user run this command

using `Docker`

```bash
docker compose exec bolt uv run manage.py createsuperuser
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

## Formulas

### Bolt

`process = CPU Cores Count`

first we need to get the how many avilable cores, in the terminal run

```bash
nproc
```

for example we get `4`, then we should set it to 4 process

### Database

`total connections = process x max_size`

let's say we have a pool with `max_size=20`, in your database run

```bash
sudo -u postgres psql
SHOW max_connections;
```

you may get `100` connections, so we should get `4 x 20 = 80 total connections` and this is less than `max_connections` witch is good, we need like from 20% => 30% avilable space for migratios or external database operations, usually a connections takes like 2 or 3 connection

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

## Docs

you can find the backend `docs` using one of the following, make sure to enable it first in `core.api`

`https://localhost/api/docs/stoplight/`

`https://localhost/api/docs/scalar/`

`https://localhost/api/docs/`

## **Enjoy**
