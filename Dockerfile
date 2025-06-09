FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    default-libmysqlclient-dev \
    libpq-dev \
    pkg-config \
    tzdata

RUN ln -s /usr/bin/python3 /usr/local/bin/python

RUN pip3 install --upgrade pip

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip install -r requirements.txt

COPY . /usr/src/app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]