# Use the official NVIDIA base image
FROM nvidia/cuda:11.4.3-cudnn8-runtime-ubuntu20.04
RUN apt-key del 7fa2af80
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu2004/x86_64/7fa2af80.pub

ENV TZ=Australia/Perth
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# Install Python 3.9 and other dependencies
RUN apt-get update && \
    apt-get install -y python3.9 python3.9-dev python3.9-distutils python3-pip \
                       libgl1-mesa-glx libglib2.0-0 libglu1-mesa  pkg-config  libhdf5-dev \
                       cuda-toolkit-11-4 libcublas-dev-11-4


# Set the working directory in the container
WORKDIR /app
# Set timezone
# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip
RUN python3.9 -m pip install --upgrade pip

RUN CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python==0.2.55 --no-cache-dir --force-reinstall --upgrade

# Install llama-cpp-python and other requirements
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.dev.txt
# Expose port 8000
EXPOSE 8000

# Copy and set permissions for the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]