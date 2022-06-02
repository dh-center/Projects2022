#!/bin/sh


if [ -f /OneMedia/BUILD_DEPLOY/ui/one-media-ui-0.0.1-SNAPSHOT.jar ]
then
   echo "Found jar"
   java -version
   export JVM_OPTIONS="$JVM_OPTIONS -Xmx1024m"
   echo "$JVM_OPTIONS"
   cd /OneMedia/BUILD_DEPLOY/ui && java -jar one-media-ui-0.0.1-SNAPSHOT.jar "${JVM_OPTIONS}"
else
  echo "Jar not found!"
   /bin/bash
fi