#!/bin/bash
set -e
set +x

cd $(dirname $0)/../..


if [ "$1" == "-f" ]; then
    rm -rf tests/e2e/data
fi

set -x

meshroom init tests/e2e/data

# PERSONA 1) Simulate a Example vendor who wants to integrate with Sekoia
cp -rf example/* tests/e2e/data

cd tests/e2e/data

# Create dummy 3rd-party product with events production capability
meshroom create product myproduct
meshroom create capability myproduct events producer --mode=push --format=json

# Create an Sekoia integration to consumer the events from myproduct
meshroom create integration sekoia myproduct events consumer --mode=push

# Create instances and plug them
set +e
pass MESHROOM_SEKOIA_API_KEY | meshroom add sekoia -s API_KEY
set -e

meshroom add myproduct
meshroom plug myproduct sekoia events
meshroom up
meshroom produce events myproduct sekoia
meshroom watch events sekoia