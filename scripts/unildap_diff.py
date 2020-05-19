import sys
from ldap_peoples import ldif

# the first is the old one
ldif_rec1 = ldif.LDIFRecordList(open(sys.argv[1]))
ldif_rec1.parse()

# the new one
ldif_rec2 = ldif.LDIFRecordList(open(sys.argv[2]))
ldif_rec2.parse()

LDAP_INTERESTING_VALUES = ('userPassword',
                           'sambaNTPassword',
                           #  'schacPersonalUniqueCode',
                           #  'schacPersonalUniqueID',
                           'mail')

LDAP_CHGADD_TMPL = """dn: {}
changetype: add
"""


LDAP_CHG_TMPL = """dn: {}
changetype: modify
"""

LDAP_CHG_ADD_TMPL = """add: {}
{}-
"""

LDAP_CHG_REPL_TMPL = """replace: {}
{}-
"""

LDAP_CHG_DEL_TMPL = """delete: {}
{}-
"""

ldif1 = dict(ldif_rec1.all_records)
ldif2 = dict(ldif_rec2.all_records)

new_entries = []
mod_entries = []
for entry in ldif2:
    if entry not in ldif1:
        new_ldif = LDAP_CHGADD_TMPL.format(entry)
        for k,v in ldif2[entry].items():
            new_ldif += ''.join(['{}: {}\n'.format(k, i.decode())
                                 for i in v])

        new_entries.append((entry, new_ldif))
    else:
        check = 0
        new_ldif = LDAP_CHG_TMPL.format(entry)
        for k in LDAP_INTERESTING_VALUES:
            if not ldif2[entry].get(k):
                # it would be a "delete" but don't needed now
                continue

            check = 0
            if ldif1[entry].get(k):
                # replace
                if ldif1[entry][k] != ldif2[entry][k]:
                    new_ldif += LDAP_CHG_REPL_TMPL.format(k, ''.join(['{}: {}\n'.format(k, i.decode())
                                                                      for i in ldif2[entry][k]]))
                    check = 1
            else:
                # add
                new_ldif += LDAP_CHG_ADD_TMPL.format(k, ''.join(['{}: {}\n'.format(k, i.decode())
                                                                 for i in ldif2[entry][k]]))
                check = 1
        if check == 1:
            mod_entries.append((entry, new_ldif))

for i in mod_entries:
    print(i[1])

for i in new_entries:
    print(i[1])

# check new entries
#  for i in ldif_rec2.all_records:
