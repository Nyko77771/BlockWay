#!/bin/bash

# Script For Creation of .env keys
# *Additionally Builds and Runs Docker (if present)

# First Checking if Docker is installed
if ! command -v docker >/dev/null 2>&1; then
    echo 'Docker is not found'
    echo 'Please Install Docker Before Proceeding'
    exit
else
    echo 'Docker Found'
    echo 'Version:'
    docker --version



if ! docker compose version >/dev/null 2>&1; then
    echo 'Docker Compose not found'
    echo 'Please Install Docker Compose Before Proceeding'
    exit
else
    echo 'Docker Compose Found'
    echo 'Version:'
    docker compose version



echo 'Creating .env file'

if [ -e .env ]; then
    echo 'File Found'
else
    echo 'Making .env'

    cat << EOF >> .env

PASSWORD=$(openssl rand -base64 12)
SECRET=$(openssl rand -base64 32)

EOF

    echo 'Created .env file'

    docker compose build --no-cache

    docker compose up

    echo 'Access your Pihole on https://pihole.localhost'

    echo ' Access your dashboard on https://block_way.localhost'

    echo 'NOTE: Make Sure to Add pihole.localhost and block-way.localhost to hosts under this machines IP'

fi



