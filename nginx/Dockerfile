# Используем официальный образ Nginx
FROM nginx:latest

RUN mkdir -p /app/staticfiles

COPY nginx.conf /etc/nginx/nginx.conf

# Открываем порт 80 для HTTP-трафика
EXPOSE 80
