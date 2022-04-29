#!/bin/bash

# remove default nginx config. Required step
rm -f /etc/nginx/conf.d/default.conf

# https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
bash -c "/usr/bin/wait-for-it.sh livedata:8000 --timeout=300"
