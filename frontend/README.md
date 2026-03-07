# FrontEnd

## OpenAPI

to update `openAPI` support run this command

```bash
bunx openapi-typescript http://localhost/api/schema/ -o app/generated/api_types.ts
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

for farther informations, see the `README.md` inside the `backend` folder
