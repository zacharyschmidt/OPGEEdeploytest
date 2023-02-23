
FROM python:3.10-slim-bullseye

RUN apt update
RUN apt-get -y install git && \
    apt-get install -y gcc


RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ADD ./requirements.txt /usr/src/app/requirements.txt

RUN pip install --upgrade pip

RUN pip install pint
RUN pip install pint-pandas

RUN pip install -r requirements.txt

COPY . /usr/src/app
COPY OPGEEv4/opgee/etc/opgee.cfg /root/opgee.cfg

#RUN git clone https://github.com/Stanford-EAO/OPGEEv4.git /usr/src/app/OPGEEv4
RUN pip install -e /usr/src/app/OPGEEv4

