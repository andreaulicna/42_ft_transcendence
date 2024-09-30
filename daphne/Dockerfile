FROM alexshin/docker-django-asgi-daphne

ENV DAPHNE_PORT=9000
ENV DJANGO_SETTINGS_MODULE=mysite.settings
ENV APP_ASGI_ENTRYPOINT=mysite.asgi:application

WORKDIR /app
# Copy the content of the local src directory to the working directory
COPY . .

CMD ["daphne", "mysite.asgi:application", "--bind", "0.0.0.0:9000", "--proxy-headers"]