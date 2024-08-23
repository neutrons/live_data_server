#!/usr/bin/env bash
. /opt/conda/etc/profile.d/conda.sh
printf "=%.0s" {1..88}
printf "\nStarting periodic purge - $(date)\n"
conda run -n livedata python /var/www/livedata/app/manage.py purge_expired_data
printf "=%.0s" {1..88}; printf "\n"
