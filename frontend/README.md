# FrontEnd

## OpenAPI

to update `openAPI` support run this command

```bash
bunx openapi-typescript http://localhost/api/openapi.json -o app/generated/api_types.ts
```

## GraphQL

to update the `GraphQL` support run this command

```bash
bunx graphql-codegen
```

## Starting Server

to start multible servers run them in a diffrent ports like this

```bash
PORT=3000 bun alone
```

then add these ports inside the `nginx` configs like this

```nginx
upstream nextjs_cluster {
    server localhost:3000;
    server localhost:3001;
    server localhost:3002;
    # ...
}
```

it's prefered to add a `systemd` service like this

```ini
[Unit]
Description=Next.js App on Port 3000
After=network.target

[Service]
User=kali
Group=www-data
WorkingDirectory=/home/kali/BdayaTeam/frontend/
ExecStart=/home/kali/.bun/bin/bun alone
Restart=always
RestartSec=3

Environment="PORT=3000" # add your PORT
Environment="NODE_ENV=production"

[Install]
WantedBy=multi-user.target
```

then you can run them both on startup like this

```bash
sudo systemctl daemon-reload
sudo systemctl enable nextjs-3000 nextjs-3001 nextjs-3002 nextjs-3004
sudo systemctl start nextjs-3000 nextjs-3001 nextjs-3002 nextjs-3004
```

for farther informations, see the `README.md` inside the `backend` folder
