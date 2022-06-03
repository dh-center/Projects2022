#!/bin/sh

set -e

echo "Current location: $(pwd)"
(cd ../../JAVA_APPS/one-media-ui && mvn clean install)
ls -alh ../../JAVA_APPS/one-media-ui/target
echo "Move jar"
mv ../../JAVA_APPS/one-media-ui/target/one-media-ui-0.0.1-SNAPSHOT.jar .