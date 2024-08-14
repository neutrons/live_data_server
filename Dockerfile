FROM continuumio/miniconda3:23.10.0-1

COPY environment.yml .
RUN conda env create

WORKDIR /var/www/livedata

COPY docker-entrypoint.sh /usr/bin/

COPY src app
RUN mkdir ./static

RUN chmod +x /usr/bin/docker-entrypoint.sh
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "livedata", "/usr/bin/docker-entrypoint.sh"]
