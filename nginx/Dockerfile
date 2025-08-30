# Используем официальный образ Nginx
FROM nginx:alpine

# Удаляем дефолтный конфиг
RUN rm /etc/nginx/conf.d/default.conf

# Копируем наш конфиг в правильную директорию
COPY nginx.conf /etc/nginx/conf.d/

# Создаем директории для статики
RUN mkdir -p /app/staticfiles /app/media

# Открываем порт 80 для HTTP-трафика
EXPOSE 80
