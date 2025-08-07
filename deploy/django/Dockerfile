FROM ghcr.io/prefix-dev/pixi:0.50.2-jammy AS base

### System dependencies and cron job setup
RUN apt-get update -y && \
    # apt upgrade -y && \
    apt-get install -y \
    vim cron wget

# Set up cron job to purge expired data once a month
COPY scripts/periodic-purge.sh /var/opt/
RUN echo "0 0 1 * * /var/opt/periodic-purge.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/root && \
    chmod 0644 /etc/cron.d/root && \
    crontab /etc/cron.d/root && \
    touch /var/log/cron.log

### Environment setup
FROM base AS build

COPY pixi.lock .
COPY pyproject.toml .
RUN pixi install --locked -e deploy

WORKDIR /var/www/livedata
COPY src app
RUN mkdir ./static

### Final image
FROM build AS final

COPY deploy/django/docker-entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/docker-entrypoint.sh
ENTRYPOINT ["pixi", "run" , "-e", "deploy", "/usr/bin/docker-entrypoint.sh"]
