FROM node:20-alpine AS build

WORKDIR /app
COPY frontend/package.json /app/package.json
COPY frontend/index.html /app/index.html
COPY frontend/vite.config.js /app/vite.config.js
COPY frontend/src /app/src
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm install && npm run build

FROM nginx:1.25-alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

