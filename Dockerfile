FROM centos:centos7

RUN yum update -y
RUN yum install -y \
    which \
    epel-release
RUN yum install -y \
    gcc \
    make \
    httpd \
    mod_wsgi \
    python-pip \
    postgresql \
    postgresql-devel \
    python-devel

WORKDIR /var/www/livedata

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY live_data_server app
RUN mkdir ./static
