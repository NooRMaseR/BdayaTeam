#!/bin/bash

set -e
echo "starting Setup"

# check for updates
sudo apt update && sudo apt upgrade -y

# setup postgresql
sudo apt install postgresql -y
sudo service postgresql start

sudo -u postgres psql -c "CREATE DATABASE teambdayadb;"
sudo -u postgres psql -c "CREATE USER team WITH PASSWORD 'team111213';"
sudo -u postgres psql -c "ALTER ROLE team SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE team SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE team SET timezone TO 'Africa/Cairo';"
sudo -u postgres psql -c "ALTER USER team CREATEDB;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE teambdayadb TO team;"
sudo -u postgres psql -d teambdayadb -c "GRANT ALL PRIVILEGES ON SCHEMA public TO team;"

sudo systemctl enable postgresql
sudo systemctl start postgresql

# setup uv
curl -LsSf https://astral.sh/uv/install.sh | sh

cd /home/$USER/BdayaTeam/backend
/home/$USER/.local/bin/uv sync --locked --no-dev

/home/$USER/.local/bin/uv run manage.py makemigrations
/home/$USER/.local/bin/uv run manage.py migrate
/home/$USER/.local/bin/uv run manage.py collectstatic --no-input


# setup redis
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server

cat <<EOF | sudo tee -a /etc/sysctl.conf
vm.overcommit_memory = 1
net.core.somaxconn=4096
net.core.netdev_max_backlog=4096
EOF

sudo sysctl -p

# setup huey
cat <<EOF | sudo tee /etc/systemd/system/huey-worker.service
[Unit]
Description=huey Worker
After=network.target redis-server.service bolt.service

[Service]
User=$USER
Group=$USER
WorkingDirectory=/home/$USER/BdayaTeam/backend
ExecStart=/home/$USER/.local/bin/uv run manage.py run_huey
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable huey-worker
sudo systemctl start huey-worker

# setup systemd for django-bolt
cat <<EOF | sudo tee /etc/systemd/system/bolt.service 
[Unit]
Description=bolt daemon
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/home/$USER/BdayaTeam/backend/
ExecStart=/home/$USER/BdayaTeam/backend/.venv/bin/python \
        manage.py \
        runbolt \
        --processes ${nproc} \
        --keep-alive 10

[Install]
WantedBy=multi-user.target
EOF

# setup systemd for daphne

cat <<EOF | sudo tee /etc/systemd/system/daphne.service 
[Unit]
Description=daphne daemon
After=network.target

[Service]
User=kali
Group=www-data
WorkingDirectory=/home/kali/BdayaTeam/backend/
ExecStart=/home/kali/BdayaTeam/backend/.venv/bin/daphne \
        -u /tmp/daphne.sock \
        BdayaTeam.asgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable bolt daphne
sudo systemctl start bolt daphne

# setup nginx
sudo apt install nginx

sudo ln -sf /home/$USER/BdayaTeam/nginx_teamBdaya.conf /etc/nginx/sites-enabled/nginx_teamBdaya.conf

sudo apt-get install acl

setfacl -m u:www-data:x /home/$USER/
setfacl -m u:www-data:x /home/$USER/BdayaTeam/
setfacl -m u:www-data:x /home/$USER/BdayaTeam/nginx_teamBdaya.conf
setfacl -m u:www-data:x /home/$USER/BdayaTeam/backend/
setfacl -m u:www-data:x /home/$USER/BdayaTeam/frontend/
setfacl -m u:www-data:x /home/$USER/BdayaTeam/backend/static_files/
setfacl -m u:www-data:x /home/$USER/BdayaTeam/backend/media_files/
setfacl -R -m u:www-data:rX /home/$USER/BdayaTeam/nginx_teamBdaya.conf
setfacl -R -m u:www-data:rX /home/$USER/BdayaTeam/backend/static_files
setfacl -R -m u:www-data:rX /home/$USER/BdayaTeam/backend/media_files
setfacl -R -m u:www-data:rX /home/$USER/BdayaTeam/frontend

/home/$USER/.local/bin/uv run manage.py test

# Frontend Setup
cd /home/$USER/BdayaTeam/frontend
sudo apt install unzip -y
curl -fsSL https://bun.com/install | bash
/home/$USER/.bun/bin/bun --version

/home/$USER/.bun/bin/bun install
/home/$USER/.bun/bin/bun run build:pack

cat <<EOF | sudo tee /etc/systemd/system/nextjs-3000.service
[Unit]
Description=Next.js App on Port 3000
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/home/$USER/BdayaTeam/frontend/
ExecStart=/home/$USER/.bun/bin/bun alone
Restart=always
RestartSec=3

Environment="PORT=3000"
Environment="NODE_ENV=production"

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF | sudo tee /etc/systemd/system/nextjs-3001.service
[Unit]
Description=Next.js App on Port 3001
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/home/$USER/BdayaTeam/frontend/
ExecStart=/home/$USER/.bun/bin/bun alone
Restart=always
RestartSec=3

Environment="PORT=3001"
Environment="NODE_ENV=production"

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF | sudo tee /etc/systemd/system/nextjs-3002.service
[Unit]
Description=Next.js App on Port 3002
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/home/$USER/BdayaTeam/frontend/
ExecStart=/home/$USER/.bun/bin/bun alone
Restart=always
RestartSec=3

Environment="PORT=3002"
Environment="NODE_ENV=production"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable nextjs-3000 nextjs-3001 nextjs-3002
sudo systemctl start nextjs-3000 nextjs-3001 nextjs-3002

echo "Setup Completed....."