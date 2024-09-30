# Stage 1: Build environment
FROM python:3.9-slim as build

WORKDIR /app


# Copy the requirements file
COPY requirements.txt .

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime environment
FROM python:3.9-slim

ENV DAPHNE_PORT=9000
ENV DJANGO_SETTINGS_MODULE=mysite.settings
ENV APP_ASGI_ENTRYPOINT=mysite.asgi:application

WORKDIR /app

# Copy the dependencies from the build stage
COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy the rest of the application code
COPY . .

# Run database migrations
#RUN python manage.py migrate

CMD ["daphne", "-b", "0.0.0.0", "-p", "9000", "mysite.asgi:application"]