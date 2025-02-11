# Use the official Python image from the DockerHub
FROM python:3.11-alpine

RUN adduser --system --no-create-home django_nonroot

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in docker
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

USER django_nonroot
# Specify the command to run on container start
CMD ["daphne", "-b", "0.0.0.0", "-p", "8005", "tournament.asgi:application"]
