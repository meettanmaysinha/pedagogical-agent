# A dockerfile must always start by importing the base image.
# We use the keyword 'FROM' to do that.
# In our example, we want import the python image.
# So we write 'python' for the image name and 'latest' for the version.
FROM python:3.11

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies
# Added libgl1-mesa-glx for OpenCV
# Combined apt-get update and install, and added cleanup
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    libgl1-mesa-glx \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files from the host (project root) to the container's WORKDIR
# Changed from COPY ../ ./ to COPY . .
COPY . .

# We need to define the command to launch when we are going to run the image.
# We use the keyword 'CMD' to do that.
# The following command will execute "python streammain.py" (assuming streammain.py is now in /usr/src/app).
CMD [ "python", "streammain.py" ]

# Run this in Command Line to build:
# (Assuming this Dockerfile is in a 'docker' subdirectory of your project)
# docker build -f docker/Dockerfile -t your-image-name .

# Run this in Command Line to run image:
# (You'll need to add port mapping, see below)
# docker run -it -p <HOST_PORT>:<CONTAINER_PORT> your-image-name