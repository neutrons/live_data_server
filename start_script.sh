#!/bin/sh
set -e

# Build the project
cd /usr/src; make install

# Start the server
apachectl restart