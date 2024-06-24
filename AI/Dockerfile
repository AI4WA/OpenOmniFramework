FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install llama-cpp-python==0.2.55 --no-cache-dir --force-reinstall --upgrade
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
