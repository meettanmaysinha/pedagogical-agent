# A dockerfile must always start by importing the base image.
# We use the keyword 'FROM' to do that.
# In our example, we want import the python image.
# So we write 'python' for the image name and 'latest' for the version.
FROM python:3.11

# Set the working directory in the container
WORKDIR /usr/src/app

# Dependency for PyAudio Library
RUN apt-get update && apt-get install -y portaudio19-dev

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy all source files from the host to the container
COPY ../ ./

# We need to define the command to launch when we are going to run the image.
# We use the keyword 'CMD' to do that.
# The following command will execute "python ../streammain.py".
CMD [ "python", "streammain.py" ]

# Run this in Command Line to build: 
# docker build -f docker/Dockerfile -t your-image-name .

# Run this in Command Line to run image:
# docker run -it your-image-name