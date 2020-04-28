import os
from subprocess import run, PIPE

CHUNKS = 5
FILE = 'ldap_importable.20200427.1754.ldif.fixed'

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


# for i in *ldif.fixed.* ; do (ldapadd -Y EXTERNAL -H ldapi:/// -c -f $i > ldapadd.log.$i &) ; done
# ps ax | grep ldif.fixed | awk -F' ' {'print $1'} | xargs kill -TERM



#run(['grep', 'f'], stdout=PIPE,
        #input='one\ntwo\nthree\nfour\nfive\nsix\n', encoding='ascii')
