FROM node:18-alpine AS builder
WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app

COPY --from=builder /app/build ./build
COPY server.js ./

EXPOSE 3000

CMD ["node", "server.js"]
