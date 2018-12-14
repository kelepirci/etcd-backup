FROM python:2.7-alpine3.6

WORKDIR /app

RUN apk update
RUN apk add wget

COPY requirements.txt ./
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN wget https://github.com/etcd-io/etcd/releases/download/v3.3.10/etcd-v3.3.10-linux-amd64.tar.gz
RUN tar -zxvf etcd-v3.3.10-linux-amd64.tar.gz etcd-v3.3.10-linux-amd64/etcdctl
RUN mv etcd-v3.3.10-linux-amd64/etcdctl /usr/local/bin
RUN rm -rf etcd-v3.3.10-linux-amd64*

COPY etcd-backup.py /app/etcd-backup.py
