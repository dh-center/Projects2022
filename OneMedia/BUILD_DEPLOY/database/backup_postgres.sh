
# https://linuxize.com/post/cron-jobs-every-5-10-15-minutes/
# Get access to crontab (sudo)
# sudo crontab -e
# 0 5 * * * cd /home/onemedia/OneMedia/BUILD_DEPLOY/database/backup && sudo  chmod 777 . && docker exec -i one_media_db /usr/bin/pg_dump -U postgres --data-only | gzip -9 > postgres-backup-tmp.sql.gz && mv postgres-backup-tmp.sql.gz postgres-backup.sql.gz

# https://simplebackups.io/blog/docker-postgres-backup-restore-guide-with-examples/
# backup concrete database
# docker exec -i postgres /usr/bin/pg_dump -U <postgresql_user> <postgresql_database> | gzip -9 > postgres-backup.sql.gz
# sql_scripts_OneMedia_1 <-- container name
#docker exec -i one_media_db /usr/bin/pg_dump -U postgres --data-only | gzip -9 > postgres-backup.sql.gz
docker exec -i one_media_db /usr/bin/pg_dump -U postgres | gzip -9 > postgres-backup.sql.gz

# backup all databases
# docker exec -i postgres /usr/bin/pg_dumpall -U <postgresql_user> > postgres-backup.sql


# restore
# docker cp </path/to/dump/in/host> <container_name>:<path_to_volume>

# docker exec one_media_db mkdir backups
# docker cp postgres-backup.sql one_media_db:/backups/
# docker exec -it one_media_db bash
# psql -U postgres -d postgres -f /backups/postgres-backup.sql
# to see real error (https://stackoverflow.com/questions/20427689/psql-invalid-command-n-while-restore-sql/20428547)
# psql -v ON_ERROR_STOP=1 -U postgres -d postgres -f /backups/postgres-backup.sql

# DO NOT FORGET to delete all rows from stat_alive table

# pg_restore -U <database_owner> -d <database_name> <path_to_dump>
# pg_restore -U postgres -d postgres /backups/postgres-backup.sql
# docker exec <container_name> <some_command>