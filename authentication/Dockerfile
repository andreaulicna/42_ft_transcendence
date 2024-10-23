# Use the official Python image from the DockerHub
FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in docker
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh
# #RUN chown app /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]

# # Specify the command to run on container start
CMD ["gunicorn", "authentication.wsgi:application", "--bind", "0.0.0.0:8002", "--reload"]
# CMD ["python", "manage.py", "runserver" , "0.0.0.0:8000"]