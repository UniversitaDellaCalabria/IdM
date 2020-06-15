#!/bin/bash

PROJ_NAME=identita_unical
PROJ_PATH=/opt/$PROJ_NAME
ENV_PATH=/opt/identita_unical.env
export DJANGO_SETTINGS_MODULE="django_idm.settings"

cd $PROJ_PATH

PASSWORD=$($ENV_PATH/bin/python3 -c "from django.conf import settings; print(settings.DATABASES['default']['PASSWORD'])")
USERNAME=$($ENV_PATH/bin/python3 -c "from django.conf import settings; print(settings.DATABASES['default']['USER'])")
DB=$($ENV_PATH/bin/python3 -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])")

LDAP_PASSWORD=$($ENV_PATH/bin/python3 -c "from django.conf import settings; print(settings.DATABASES['ldap']['PASSWORD'])")
LDAP_USERNAME=$($ENV_PATH/bin/python3 -c "from django.conf import settings; print(settings.DATABASES['ldap']['USER'])")
#LDAP_BASE=$($ENV_PATH/bin/python3 -c "from django.conf import settings; print(settings.LDAP_PEOPLE_DN)")
LDAP_BASE=$($ENV_PATH/bin/python3 -c "from django.conf import settings; print(settings.LDAP_BASEDN)")


BACKUP_DIR="/opt/dumps_$PROJ_NAME"
BACKUP_DIR_LDIF=$BACKUP_DIR"/ldif"
BACKUP_DIR_JSON=$BACKUP_DIR"/json"
BACKUP_DIR_SQL=$BACKUP_DIR"/sql"
BACKUP_DIR_MEDIA=$BACKUP_DIR"/media"
FNAME="$PROJ_NAME.$(date +"%Y-%m-%d_%H%M%S")"

# sudo apt install p7zip-full
mkdir -p $BACKUP_DIR
mkdir -p $BACKUP_DIR_LDIF
mkdir -p $BACKUP_DIR_JSON
mkdir -p $BACKUP_DIR_SQL
mkdir -p $BACKUP_DIR_MEDIA

set -x
set -e



# LDIF
ldapsearch -LLL -H ldap:/// -D "$LDAP_USERNAME" -w "$LDAP_PASSWORD" -b "$LDAP_BASE" + '*' | 7z a $BACKUP_DIR_LDIF/$FNAME.ldap_people.ldif.7z -si -p$PASSWORD

# JSON LDAP
$ENV_PATH/bin/python3 $PROJ_PATH/manage.py shell -c  '
from django.conf import settings
from ldap_peoples.models import *

settings.LDAP_SEARCH_LIMIT = None
peoples = LdapAcademiaUser.objects.all()
for pe in peoples:
    print(pe.json(), end="")
' | 7z a $BACKUP_DIR_JSON/$FNAME.ldap_people.json.7z -si -p$PASSWORD

# clear expired sessions
$ENV_PATH/bin/python3 $PROJ_PATH/manage.py  clearsessions

# JSON dump, encrypt and compress
$ENV_PATH/bin/python3 $PROJ_PATH/manage.py dumpdata --exclude auth.permission --exclude contenttypes --exclude sessions --indent 2  | 7z a $BACKUP_DIR_JSON/$FNAME.json.7z -si -p$PASSWORD

# SQL dump, encrypt and compress
mysqldump -u $USERNAME --password=$PASSWORD $DB | 7z a $BACKUP_DIR_SQL/$FNAME.sql.7z -si -p$PASSWORD

# decrypt
# 7z x $BACKUP_DIR/$FNAME.7z -p$PASSWORD

# media files
# [ -d "$PROJ_PATH/data/media" ] && rsync -avu --delete $PROJ_PATH/data/media $BACKUP_DIR_MEDIA
[ -d "$PROJ_PATH/data/media" ] && rsync -avu $PROJ_PATH/data/media $BACKUP_DIR_MEDIA
