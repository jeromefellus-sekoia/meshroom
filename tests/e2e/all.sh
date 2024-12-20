#!/bin/bash
set -x

cd $(dirname $0)/../..


if [ "$1" == "-f" ]; then
    rm -rf tests/e2e/data
fi

meshroom init tests/e2e/data

# PERSONA 1) Simulate a vendor who defines the Sekoia product
cp -rf example/* tests/e2e/data

cd tests/e2e/data
meshroom pull sekoia

# PERSONA 2) The end user experience starts here

meshroom add sekoia

meshroom list products sek
meshroom list tenants sek

meshroom list integrations sekoia

meshroom add apache_http_server
meshroom add aws_vpc_flow_logs aws

meshroom plug apache_http_server sekoia events
meshroom plug aws sekoia events

meshroom up

meshroom down

meshroom up
