FROM nginxinc/nginx-unprivileged:alpine3.20

# RUN adduser --system --no-create-home nginx_nonroot

# RUN rm /etc/nginx/conf.d/default.conf && \
#     mkdir -p /var/www/ft_transcendence/

COPY nginx.conf /etc/nginx/conf.d
COPY . /var/www/ft_transcendence/

# RUN rm -f /var/www/ft_transcendence/nginx.conf
# USER nginx_nonroot
# CMD ["nginx","-g","daemon off;"]