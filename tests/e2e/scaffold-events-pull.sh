#!/bin/bash
set -x

cd $(dirname $0)/../..


if [ "$1" == "-f" ]; then
    rm -rf tests/e2e/data
fi

meshroom init tests/e2e/data

# PERSONA 1) Simulate a Example vendor who wants to integrate with Sekoia
cp -rf example/* tests/e2e/data

cd tests/e2e/data

# Create dummy 3rd-party product
meshroom create product example

# Create custom integration
meshroom create integration sekoia example events consumer --mode=pull
meshroom create capability example events producer --mode=pull --format=json

# Create tenants and plug them
pass MESHROOM_SEKOIA_API_KEY | meshroom add sekoia -s API_KEY
meshroom add example
meshroom plug example sekoia events

# Add git remote to all syncing custom module from git repo
git add .
git commit -a -m "Initial commit"
git remote add origin git@github.com:jeromefellus-sekoia/test-meshroom-custom-integration1.git
git branch
git push -f -u origin master

meshroom up