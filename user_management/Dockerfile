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

COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh && \
	chmod +x /entrypoint.sh && \
	chown django_nonroot /entrypoint.sh

RUN mkdir -p /app/mediafiles && chown django_nonroot /app/mediafiles

USER django_nonroot
ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8001", "user_management.asgi:application"]
