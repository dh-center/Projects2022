#!/bin/sh

if [ -f /OneMedia/APPS/tlg/bot/sessions/client_account_manager.session ]
then
   echo "Bot session found"
   cd /OneMedia/APPS/tlg/bot && python bot_app.py
else
   /bin/bash
fi