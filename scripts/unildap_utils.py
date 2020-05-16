import copy
import datetime
import json
import re
import sys

from ldap_peoples import ldif

SCHAC_HOMEORG = 'unical.it'

LDIF_TMPL = """{dn}
objectclass: inetOrgPerson
objectclass: organizationalPerson
objectclass: person
objectclass: userSecurityInformation
objectclass: eduPerson
objectclass: radiusprofile
objectclass: sambaSamAccount
objectclass: schacContactLocation
objectclass: schacEmployeeInfo
objectclass: schacEntryConfidentiality
objectclass: schacEntryMetadata
objectclass: schacExperimentalOC
objectclass: schacGroupMembership
objectclass: schacLinkageIdentifiers
objectclass: schacPersonalCharacteristics
objectclass: schacUserEntitlements
{uid}
{cn}
{givenName}
{sn}
{displayName}
{userPassword}
{eduPersonPrincipalName}
{eduPersonAffiliation}
{eduPersonScopedAffiliation}
{eduPersonEntitlement}
{schacHomeOrganization}
schacHomeOrganizationType: urn:schac:homeOrganizationType:IT:educationInstit
 ution
schacHomeOrganizationType: urn:schac:homeOrganizationType:IT:university
"""

LDIF_STAFF_ATTR = """eduPersonEntitlement: urn:mace:terena.org:tcs:escience-user
eduPersonEntitlement: urn:mace:terena.org:tcs:personal-user
"""
eduPersonEntitlement = [b'urn:mace:dir:entitlement:common-lib-terms']
eduPersonEntitlement_staff = [b'urn:mace:terena.org:tcs:escience-user',
                              b'urn:mace:terena.org:tcs:personal-user']

# also, telephoneNumber: 0984496945
LDIF_EXT_ATTR = """schacDateOfBirth: 19850809
schacPlaceOfBirth: IT,Cosenza
schacExpiryDate: 20200814101604Z
"""

EXCLUDED_DN = ['ou=People,dc=unical,dc=it',
               'ou=studenti,ou=People,dc=unical,dc=it',
               'ou=personale,ou=People,dc=unical,dc=it']

DN_REGEXP = 'uid=[A-Za-z0-9\-\.\_]*,ou=(studenti|personale),ou=people,dc=unical,dc=it'


def filter_dn(entries, regexp=DN_REGEXP):
    filtered_entries = []
    missings = []
    for entry in entries:
        entry = list(entry)
        entry[0] = entry[0].lower()
        res = re.match(regexp, entry[0])
        if res:
            filtered_entries.append(entry)
        else:
            missings.append(entry[0])
    return filtered_entries, missings


def get_duplicates_by_attribute(entries, attribute):
    unique_codes = dict()
    duplicates = dict()
    for i in entries:
        dn = i[0]
        ucodes = i[1].get(attribute)
        if not ucodes: continue
        for ucode in ucodes:
            ucode = ucode.lower()
            if ucode not in unique_codes.keys():
                unique_codes[ucode] = dn
            else:
                if duplicates.get(ucode):
                    values = duplicates[ucode]
                else:
                    values = [unique_codes[ucode]]
                values.append(dn)
                duplicates[ucode] = values
    return duplicates


def repr_duplicates(dup):
    rows = []
    if isinstance(dup, dict):
        for k,v in dup.items():
            row = '{}\n{}\n-------------\n'.format(k.decode(),
                                                   '\n'.join(v))
            rows.append(row)
    elif isinstance(dup, list):
        for i in dup:
            row = '{}\n'.format(i)
            rows.append(row)
    else:
        raise Exception('Should be a dict or a list')
    return tuple(rows)


def print_duplicates(dup):
    print(''.join(repr_duplicates(dup)))


def dump_duplicates(dup, fpath):
    f = open(fpath, 'w')
    f.write(''.join(repr_duplicates(dup)))
    return fpath


def get_new_ldif(entry, mail=True, cf=True, code=True):
    dentr = copy.copy(entry[1])
    dn = entry[0]
    cleaned_dn = dn.lower().\
                      replace('ou=personale,', '').\
                      replace('ou=studenti,', '').\
                      replace('ou=People,', 'ou=people,')
    dentr['dn'] = [cleaned_dn.encode(),]
    dentr['uid'] = [dentr['uid'][0].lower()]
    dentr['schacHomeOrganization'] = [SCHAC_HOMEORG.encode(),]
    dentr['eduPersonScopedAffiliation'] = []
    dentr['eduPersonEntitlement'] = []
    dentr['eduPersonEntitlement'].extend(eduPersonEntitlement)
    affdec = [i.decode() for i in dentr['eduPersonAffiliation']]
    if 'staff' in affdec:
        dentr['eduPersonEntitlement'].extend(eduPersonEntitlement_staff)
    elif 'student' in affdec:
        dentr['sambaSID'] = ['{}@studenti.unical.it'.format(
                                dn[4:].partition(',')[0]
                                ).encode()]
    if dentr.get('mail'):
        if mail:
            dentr['mail'] = [i.lower() for i in dentr['mail']]
        else:
            del(dentr['mail'])

    for aff in dentr['eduPersonAffiliation']:
        scopaff = '{}@{}'.format(aff.decode(), SCHAC_HOMEORG)
        if scopaff not in dentr['eduPersonScopedAffiliation']:
            dentr['eduPersonScopedAffiliation'].append(scopaff.encode())
    new_entry = dict()
    for k,val in dentr.items():
        new_entry[k] = '\n'.join(['{}: {}'.format(k, subval.decode())
                                  for subval in val])
    res = LDIF_TMPL.format(**new_entry)
    if new_entry.get('sambaNTPassword'):
        res += '{}\n'.format(new_entry['sambaNTPassword'])
    if mail and dentr.get('mail'):
        res += '{}\n'.format(new_entry['mail'])
    if cf and new_entry.get('schacPersonalUniqueID'):
        res += '{}\n'.format(new_entry['schacPersonalUniqueID'])
    if new_entry.get('sambaSID'):
        res += '{}\n'.format(new_entry['sambaSID'].lower())
    if code and new_entry.get('schacPersonalUniqueCode'):
        res += '{}\n'.format(new_entry['schacPersonalUniqueCode'])
    return res


def decode_entry(entry):
    dentr = copy.copy(entry[1])
    ne = {}
    for k,v in dentr.items():
        ne[k] = [i.decode() for i in v]
    ne['dn'] = entry[0]
    ne.pop('objectClass')
    return ne

# the more used password
def get_most_used_passwd(dup_passwd):
    cnt = []
    that = ''
    for k,v in dup_passwd.items():
        if len(v) > len(cnt):
            cnt.extend(v)
            that = k

fopen = open(sys.argv[1])
ldif_rec = ldif.LDIFRecordList(fopen)
ldif_rec.parse()

entries, missings = filter_dn(ldif_rec.all_records)
duplicates_emails = get_duplicates_by_attribute(entries, 'mail')
duplicates_schacuid = get_duplicates_by_attribute(entries,
                                                  'schacPersonalUniqueID')
duplicates_schacucode = get_duplicates_by_attribute(entries,
                                                    'schacPersonalUniqueCode')
duplicates_uid = get_duplicates_by_attribute(entries, 'uid')
#  duplicates_passwd = get_duplicates_by_attribute(entries, 'sambaNTPassword')

# Without uniqueID
without_uniqueid = []
for i in entries:
    if 'schacPersonalUniqueID' not in i[1].keys():
        without_uniqueid.append(i[0])
        continue
    for e in i[1]['schacPersonalUniqueID']:
        if len(e) < 38:
            without_uniqueid.append(i[0])

# Without samba password
without_eduroam = []
for i in entries:
    if 'sambaNTPassword' not in i[1].keys():
        without_eduroam.append(i[0])

# invalid uid
invalid_uids = []
for i in entries:
    if 'aaaaa' in i[0].lower():
        invalid_uids.append(i[0])

EXCLUDED_DN.extend(invalid_uids)

# those who have: schacpersonaluniqueid: urn:schac:personaluniqueid:it:cf:
EXCLUDED_DN.extend(without_uniqueid)
# import they as they are ...
#EXCLUDED_DN.extend(without_eduroam)

duplicates_emails_list = list(duplicates_emails.values())
duplicates_schacuid_list = []
for i in duplicates_schacuid.values():
    duplicates_schacuid_list.extend(i)
duplicates_schacucode_list = []
for i in duplicates_schacucode.values():
    duplicates_schacucode_list.extend(i)

duplicates = [i for i in duplicates_emails_list]
duplicates.extend(duplicates_schacuid_list)
duplicates.extend(duplicates_schacucode_list )
for i in duplicates:
    EXCLUDED_DN.extend(i)
# remove duplicates
EXCLUDED_DN = list(set(EXCLUDED_DN))

# -----------------------------------------------------

now = datetime.datetime.now().strftime('%Y%m%d.%H%M')
f = open('ldap_importable.{}.ldif'.format(now), 'w')
fm = open('missing.{}.ldif'.format(now), 'w')
fdm = open('duplicated_email.{}.ldif'.format(now), 'w')
fduid = open('duplicated_uid.{}.ldif'.format(now), 'w')
fdcf = open('duplicated_cf.{}.ldif'.format(now), 'w')
fdnocf = open('without_cf.{}.ldif'.format(now), 'w')
fdmat = open('duplicated_matricola.{}.ldif'.format(now), 'w')

for entry in missings:
    if entry[:2] == 'ou': continue
    fm.write(json.dumps(entry)+'\n')
for entry, v in duplicates_emails.items():
    fdm.write('{}: {}\n'.format(entry.decode(),
                                ','.join(v)))
fdm.close()
for entry in duplicates_uid:
    fduid.write(json.dumps(decode_entry(entry))+'\n')
fduid.close()
for entry,v in duplicates_schacuid.items():
    fdcf.write('{}: {}\n'.format(entry.decode(),
                                 ','.join(v)))
fdcf.close()
for entry, v in duplicates_schacucode.items():
    fdmat.write('{}: {}\n'.format(entry.decode(),
                                  ','.join(v)))
fdmat.close()
for entry in without_uniqueid:
    fdnocf.write(entry+'\n')
fdnocf.close()

# prima i dipendenti
entries.reverse()
for entry in entries[:]:
    if entry[0] in invalid_uids: continue
    #  if 'uid=1183' in entry[0]:
        #  import pdb; pdb.set_trace()
    mail = False if entry[0] in duplicates_emails_list else True
    if 'ou=personale' in entry[0]:
        cf = True
        code = True
    else:
        if entry[0] in EXCLUDED_DN: continue
        cf = False if entry[0] in duplicates_schacuid_list else True
        code = False if entry[0] in duplicates_schacucode_list else True
    #  import pdb; pdb.set_trace()
    new_entry = get_new_ldif(entry, mail = mail,
                                    cf = cf,
                                    code = code)
    #  print(new_entry)
    f.write(new_entry+'\n')
f.close()
fm.close()
