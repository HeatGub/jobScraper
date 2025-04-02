# DOWNGRADE UBUNTU FOR SELENIUM
FROM ubuntu:22.04

# USE A PYTHON BASE IMAGE
FROM python:3.12.2

# SET THE WORKING DIRECTORY INSIDE THE CONTAINER
WORKDIR /app

# INSTALL DEPENDENCIES
COPY requirements.txt .
# exclude a line containing windows specific package pywin32 and save to ubuntuRequirements.txt
RUN grep -v 'pywin32' requirements.txt > ubuntuRequirements.txt && \
    pip install --no-cache-dir -r ubuntuRequirements.txt

# INSTALL REQUIRED SYSTEM PACKAGES
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    && rm -rf /var/lib/apt/lists/*

# INSTALL GOOGLE CHROME
RUN wget -qO- https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb > /tmp/chrome.deb \
    && apt-get update \
    && apt-get install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb

# INSTALL CHROME DRIVER
# check browser verison (3rd word recognized by awk) and save to file
RUN google-chrome --version | awk '{print $3}' > /tmp/chromeVersion.txt \
    # download matching driver by concatenating chromeversion.txt (-q = quiet, -o = output path)
    && wget -q https://storage.googleapis.com/chrome-for-testing-public/$(cat /tmp/chromeVersion.txt)/linux64/chromedriver-linux64.zip -O /tmp/chromeDriver.zip \
    # unzip downloaded file (-d = destination) - /usr/local/bin/ is a standard directory for executables. Unzipped directory name chromedriver-linux64
    && unzip /tmp/chromeDriver.zip -d /usr/local/bin/ \
    # add execution permission
    && chmod +x /usr/local/bin/chromedriver-linux64/chromedriver

# COPY APP FILES
COPY . .

# RUN FLASK
CMD ["python", "main.py"]


# https://hub.docker.com/repository/docker/letmedockerize/job_scraper/general

#################################################### BUILD AND UPLOAD IMAGE WORKFLOW ####################################################

########  0. DOCKERIZE_MODE_ACTIVE = True (settings.py)

#######################   1. BUILDING AN IMAGE
# docker build -t job_scraper .
#######################   2. RUNNING CONTAINER (not yet tagged and uploaded)
# docker run -p 5000:5000 job_scraper
    # FOR INTERACTIVE BASH MODE
    # docker run -it job_scraper /bin/bash
#######################   3. EXITING CONTAINER
# exit (or ctrl+c in terminal)
#######################   4. UPLOADING CONTAINER (CMD)
# docker login
# docker tag job_scraper letmedockerize/job_scraper:latest
# docker push letmedockerize/job_scraper:latest
#######################      RUNNING UPLOADED CONTAINER
# docker run -p 5000:5000 letmedockerize/job_scraper:latest

########   5. DOCKERIZE_MODE_ACTIVE = False (settings.py)

#################################################### BUILD AND UPLOAD IMAGE WORKFLOW ####################################################


#######################      COMMANDS INFO
# docker run -p <host_port>:<container_port> <image_name>
# -p 5000:5000 → Maps port 5000 in the container to port 5000 on your machine.
# docker ps -a  # shows also finished container processes
# docker tag myapp myusername/myapp:v1

################### RESETTING DOCKER FROM TERMINAL (WINDOWS):
# net stop com.docker.service
# wsl --shutdown
# wsl
# net start com.docker.service

################### WSL INFO (Windows Subsystem for Linux)
# WSL starts with docker desktop/wsl command
# wsl --list --verbose
# wsl --list --running
    # Ubuntu (Default)
    # docker-desktop

################### DOCKER COMPOSE (discarded)
    # Build from docker-compose.yml
# docker compose up -d
    # Verify the Running Container
# docker compose ps
    # Stop container (project)
# docker compose down