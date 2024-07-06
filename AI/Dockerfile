# Use the official NVIDIA base image
FROM nvidia/cuda:11.4.3-cudnn8-runtime-ubuntu20.04

# Set the working directory in the container
WORKDIR /app
RUN apt-get update && \
    apt-get remove -y python3 && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Copy the current directory contents into the container at /app
COPY . /app
ENV TZ=Australia/Perth
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# Install Python 3.9 and other dependencies
RUN apt-get update && \
    apt-get install -y python3.9 python3.9-dev python3.9-distutils python3-pip && \
    apt-get install -y libgl1-mesa-glx libglib2.0-0  libglu1-mesa && \
    apt-get clean
#    rm -rf /var/lib/apt/lists/* \

# Upgrade pip
RUN python3.9 -m pip install --upgrade pip

# Install llama-cpp-python and other requirements
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.dev.txt
RUN pip install llama-cpp-python==0.2.55 --no-cache-dir --force-reinstall --upgrade


# Expose port 8000
EXPOSE 8000

# Copy and set permissions for the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

## Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]