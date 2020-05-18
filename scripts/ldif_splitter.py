import os
import sys
from subprocess import run, PIPE

CHUNKS = 10
FILE = sys.argv[1]

fsize = os.path.getsize(FILE)
first_block = int(fsize / CHUNKS)

f = open(FILE, 'r')
entries = f.read().split('\n\n')
f.close()

nblocks = round(len(entries) / CHUNKS)
blocks = []
block = []
cnt = 0
while entries:
    block.append(entries.pop())
    cnt += 1
    if cnt == nblocks:
        blocks.append('\n\n'.join(block).encode())
        block = []
        cnt = 0

for i in range(len(blocks)):
    f = open(FILE+'.{}'.format(i), 'wb')
    f.write(blocks[i])
    f.close()

# do a dump
# export SUFFIX = $(date +%Y%m%d.%H%M)
# ldapsearch -LLL -Y EXTERNAL -H ldapi:// -b "ou=people,dc=unical,dc=it"  > ldap_dump.$SUFFIX.ldif

# run unildap_utils.py ldap_dump.$SUFFIX.ldif

# do things
# sed -e 's\ou=personale,\\g' -e 's\ou=studenti,\\g' -e 's\ou=People,\ou=people,\g' ldap_importable.$SUFFIX.ldif > ldap_importable.$SUFFIX.ldif.fixed

# test uniqueness
# grep "mail:" ldap_importable.$SUFFIX.ldif.fixed |  uniq -d

# for i in *ldif.fixed.* ; do (ldapadd -Y EXTERNAL -H ldapi:/// -c -f $i > $i.log 2>&1 &) ; done
# ps ax | grep ldif.fixed | awk -F' ' {'print $1'} | xargs kill -TERM

# bash clean.sh
