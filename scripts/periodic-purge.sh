#!/usr/bin/env bash
printf "=%.0s" {1..88}
printf "\nStarting periodic purge - $(date)\n"
pixi run -e deploy python /var/www/livedata/app/manage.py purge_expired_data
printf "=%.0s" {1..88}; printf "\n"
