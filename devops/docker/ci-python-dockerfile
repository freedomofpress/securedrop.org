FROM python:3.4-slim

LABEL maintainer="Freedom of the Press Foundation"

RUN apt-get update &&\
    apt-get install --no-install-recommends git -y &&\
    apt-get clean && rm -rf /var/lib/apt/lists/* &&\
    rm -rf /usr/share/doc/ && rm -rf /usr/share/man &&\
    rm -rf /usr/share/locale
