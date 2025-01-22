FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf && \
    mkdir -p /var/www/ft_transcendence/

COPY nginx.conf /etc/nginx/conf.d
COPY . /var/www/ft_transcendence/

RUN rm -f /var/www/ft_transcendence/nginx.conf