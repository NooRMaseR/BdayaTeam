echo restarting Nginx and Gunicorn
sudo systemctl restart nginx gunicorn

echo going to ./frontend
cd frontend

echo rebuilding FrontEnd
bun run build

echo starting FrontEnd
bun alone

