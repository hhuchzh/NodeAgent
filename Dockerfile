# Pull base image.
FROM ubuntu:16.04
MAINTAINER Chen Zhen <zhen1.chen@samsung.com>

ENV \
  USER=root \
  LANG=en_GB \
  LANGUAGE=en_GB:en

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        python \
        python-dev \
        python-setuptools \
        python-pip \
        supervisor \
        vim \
        iproute2 && \
        rm -rf /var/lib/apt/lists/*


# Define working directory.
#RUN pip install --upgrade pip
ENV LC_ALL=C
RUN pip install flask boto3 apscheduler uwsgi

WORKDIR /data
WORKDIR /data/app

COPY NodeAgent/ /data/NodeAgent/
COPY uwsgi.ini /etc/uwsgi.ini
COPY startup.sh /data/
COPY iperf /usr/bin/iperf

RUN chmod +x /usr/bin/iperf

EXPOSE 4999
EXPOSE 29999

WORKDIR /data
#ENTRYPOINT ["./start.sh"]