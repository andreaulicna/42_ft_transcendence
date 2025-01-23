# FROM alpine:3.19

# RUN mkdir -p /home/nonroot
# RUN adduser -S -h /home/redis_nonroot redis_nonroot
# VOLUME /home/nonroot/tmp

# RUN apk update && apk upgrade && \
#     apk add --no-cache redis && \
#     sed -i "s|bind 127.0.0.1|#bind 127.0.0.1|g"  /etc/redis.conf && \
#     sed -i "s|# maxmemory <bytes>|maxmemory 20mb|g"  /etc/redis.conf && \
#     sed -i "s|protected-mode yes|protected-mode no|g"  /etc/redis.conf && \
#     echo "maxmemory-policy allkeys-lru" >> /etc/redis.conf
# 	# mkdir -p /var/log/redis /var/lib/redis /var/run/redis && \
#     # chown -R redis_nonroot /var/log/redis /var/lib/redis /etc/redis.conf

# USER redis_nonroot
# CMD [ "redis-server" , "/etc/redis.conf" ]

FROM redis:8.0-M03-alpine3.21
# RUN adduser --system --no-create-home redis_nonroot
# USER redis_nonroot
