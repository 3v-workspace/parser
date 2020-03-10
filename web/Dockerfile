FROM python:3.6

WORKDIR /app
COPY docker_django/system/requirements/ /app/docker_django/system/requirements/
RUN apt-get update &&\
    apt-get install -y build-essential g++ make binutils libproj-dev gdal-bin
RUN pip install -r docker_django/system/requirements/development.txt -r docker_django/system/requirements/production.txt
RUN apt-get install -y\
    libusb-dev libc6 liblttng-ust-dev manpages-dev manpages software-properties-common ccache g++ gcc make cmake\
    libgtk-3-dev python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info