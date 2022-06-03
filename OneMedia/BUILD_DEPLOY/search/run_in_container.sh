#!/bin/sh

if [ -f /OneMedia/BUILD_DEPLOY/search/OneMediaIndex-1.0-SNAPSHOT-all.jar ]
then
   echo "Found jar"
   java -version
   export JVM_OPTIONS="$JVM_OPTIONS --add-opens java.base/jdk.internal.misc=ALL-UNNAMED -Dio.netty.tryReflectionSetAccessible=true"
   export JVM_OPTIONS="$JVM_OPTIONS -Xmx1024m"
   echo "$JVM_OPTIONS"
   cd /OneMedia/BUILD_DEPLOY/search && java -jar OneMediaIndex-1.0-SNAPSHOT-all.jar "${JVM_OPTIONS}"
else
  echo "Jar not found!"
   /bin/bash
fi