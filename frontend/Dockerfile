FROM oven/bun:1-slim

WORKDIR /app

COPY package.json bun.lockb* ./

RUN bun install --frozen-lockfile

COPY . .

RUN bun run build:pack

EXPOSE 3000

CMD ["bun", "run", "alone"]
