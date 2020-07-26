FROM python:3.8
ENV DEBIAN_FRONTEND noninteractive
COPY . /usr/prog/
WORKDIR /usr/prog
RUN apt-get update && apt-get install -y apt-utils \
    && apt-get -y install locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

RUN apt-get install -y python3-pip python-psycopg2 && pip3 install setuptools influxdb PyQt5 pyqtgraph\
    && apt-get install -y pyqt5-dev-tools

