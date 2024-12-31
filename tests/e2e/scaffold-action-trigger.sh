#!/bin/bash
set -x
set -e

cd $(dirname $0)/../..


if [ "$1" == "-f" ]; then
    rm -rf tests/e2e/data
fi

meshroom init tests/e2e/data

# PERSONA 1) Simulate a Example vendor who wants to integrate with Sekoia
cp -rf example/* tests/e2e/data

cd tests/e2e/data

# Create 3rd-party product
meshroom create product cisa_gov

# Create custom integration
meshroom create integration sekoia cisa_gov action trigger --mode=push
meshroom create capability cisa_gov action executor --mode=push --format=json

# Create tenants and plug them
pass MESHROOM_SEKOIA_API_KEY | meshroom add sekoia -s API_KEY
meshroom add cisa_gov
meshroom plug sekoia cisa_gov action

# Add git remote to all syncing custom module from git repo
git add .
git commit -a -m "Initial commit"
git remote add origin git@github.com:jeromefellus-sekoia/test-meshroom-custom-integration-cisa.git
git branch
git push -f -u origin master

meshroom up