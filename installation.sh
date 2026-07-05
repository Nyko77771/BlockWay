#!/bin/bash

# Script For Creation of .env keys
# *Additionally Builds and Runs Docker

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

    echo ' Access your dashboard on https://block_way.localhost'

fi



