#!/bin/bash
set -x

cd $(dirname $0)/../..


rm -rf tests/e2e/data

meshroom init tests/e2e/data

# Simulate a vendor who defines the Sekoia product
cp -rf example/* tests/e2e/data

cd tests/e2e/data
meshroom pull sekoia