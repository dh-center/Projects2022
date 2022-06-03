#!/bin/sh

# about the if below : https://stackoverflow.com/questions/6363441/check-if-a-file-exists-with-wildcard-in-shell-script
if ls /OneMedia/APPS/vk/sessions/vk_config.v2* 1> /dev/null 2>&1; then
   echo "VK sessions found"
   cd /OneMedia/APPS/vk && python vk_crawler.py
else
   /bin/bash
fi
