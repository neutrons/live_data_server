FROM centos:centos7

# ENV variables that need to be updated/supplied either from CLI or
# docker-compose.yml
ENV DATABASE_NAME=livedata
ENV DATABASE_USER=postgres
ENV DATABASE_PASS=postgres
ENV DATABASE_PORT=5432
ENV DATABASE_HOST=db

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
    # postgresql-server \
    # postgresql-contrib \
    postgresql-devel \
    python-devel
RUN pip install \
    Django==1.9.12 \
    django-cors-headers==1.3.1 \
    psycopg2==2.6.2

COPY apache/apache_django_wsgi.conf /etc/httpd/conf.d/
# COPY third-party/systemctl.py /usr/bin/systemctl

WORKDIR /usr/src

# Copy source code
COPY ./live_data_server ./live_data_server
COPY ./Makefile .

# Move the entry-point into the volume
COPY ./start_script.sh /usr/bin/start_script.sh
RUN chmod +x /usr/bin/start_script.sh
CMD ["/usr/bin/start_script.sh"]