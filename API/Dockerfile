# Use an official Python runtime as a parent image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/app

# Install dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt
COPY ./requirements.dev.txt /usr/src/app/requirements.dev.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.dev.txt
# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client

# Copy the current directory contents into the container at /usr/src/app
# copy but ignore the files in .dockerignore
COPY . /usr/src/app/

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
COPY ./entrypoint_worker.sh /usr/src/app/entrypoint_worker.sh

# Make sure the script is executable
RUN chmod +x /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint_worker.sh
