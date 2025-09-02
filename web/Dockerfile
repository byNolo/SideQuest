FROM node:20-alpine as build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM busybox:stable
WORKDIR /dist
COPY --from=build /app/dist .
VOLUME /dist
