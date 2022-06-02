#!/bin/sh

if [ -f /OneMedia/APPS/tlg/extractor/sessions/extractor_session.session ]
then
   echo "Extractor session found"
   cd /OneMedia/APPS/tlg/extractor && python extractor.py
else
   /bin/bash
fi
