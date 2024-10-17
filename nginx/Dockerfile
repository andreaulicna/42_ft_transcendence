FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
RUN	mkdir -p /var/www/ft_transcendence/

COPY . /var/www/ft_transcendence/
