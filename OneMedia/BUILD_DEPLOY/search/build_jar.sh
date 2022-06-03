#!/bin/sh

set -e

echo "Current location: $(pwd)"
(cd ../../JAVA_APPS/Search && ./gradlew shadowJar)
ls -al ../../JAVA_APPS/Search/build/libs
mv ../../JAVA_APPS/Search/build/libs/OneMediaIndex-1.0-SNAPSHOT-all.jar .