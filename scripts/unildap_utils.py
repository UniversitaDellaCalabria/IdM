import copy
import re
from ldap_peoples import ldif

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
{mail}
{userPassword}
{sambaNTPassword}
{eduPersonPrincipalName}
{eduPersonAffiliation}
{eduPersonEntitlement}
schacHomeOrganization: unical.it
schacHomeOrganizationType: urn:schac:homeOrganizationType:IT:educationInstit
 ution
schacHomeOrganizationType: urn:schac:homeOrganizationType:IT:university
{schacPersonalUniqueID}
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

DN_REGEXP = 'uid=[A-Za-z0-9\-\.\_]*,ou=(studenti|personale),ou=People,dc=unical,dc=it'


def filter_dn(entries, regexp=DN_REGEXP):
    filtered_entries = []
    missings = []
    for entry in entries:
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
    for k,v in dup.items():
        print(k.decode(), '\n', '\n'.join(v), '\n--\n')


def get_new_ldif(entry):
    dentr = copy.copy(entry[1])
    dentr['dn'] = (entry[0].encode(),)
    new_entry = dict()
    dentr['eduPersonEntitlement'] = []
    dentr['eduPersonEntitlement'].extend(eduPersonEntitlement)
    if 'staff' in [i.decode() for i in dentr['eduPersonAffiliation']]:
        dentr['eduPersonEntitlement'].extend(eduPersonEntitlement_staff)
    for k,val in dentr.items():
        new_entry[k] = '\n'.join(['{}: {}'.format(k, subval.decode())
                                  for subval in val])

    return LDIF_TMPL.format(**new_entry)

# the more used password
def get_most_used_passwd(dup_passwd):
    cnt = []
    that = ''
    for k,v in dup_passwd.items():
        if len(v) > len(cnt):
            cnt.extend(v)
            that = k


fopen = open('/home/wert/ldap_dump.20200423.2348.ldif')
ldif_rec = ldif.LDIFRecordList(fopen)
ldif_rec.parse()

entries, missings = filter_dn(ldif_rec.all_records)
duplicates_emails = get_duplicates_by_attribute(entries, 'mail')
duplicates_schacuid = get_duplicates_by_attribute(entries, 'schacPersonalUniqueID')
duplicates_schacucode = get_duplicates_by_attribute(entries, 'schacPersonalUniqueCode')
duplicates_uid = get_duplicates_by_attribute(entries, 'uid')
duplicates_passwd = get_duplicates_by_attribute(entries, 'sambaNTPassword')

# Without uniqueID
without_uniqueid = []
for i in entries:
    if 'schacPersonalUniqueID' not in i[1].keys():
        without_uniqueid.append(i[0])

# Without samba password
without_eduroam = []
for i in entries:
    if 'sambaNTPassword' not in i[1].keys():
        without_eduroam.append(i[0])

EXCLUDED_DN.extend(without_eduroam)
EXCLUDED_DN.extend(without_uniqueid)

# i colleghi con le email duplicate non posso importarli
duplicates = list(duplicates_emails.values())
duplicates.extend(duplicates_schacuid.values())
duplicates.extend(duplicates_schacucode.values())
for i in duplicates:
    EXCLUDED_DN.extend(i)

#uids = tuple([i[0] for i in ldif_rec.all_records])

# remove duplicates
EXCLUDED_DN = list(set(EXCLUDED_DN))

for entry in entries[:]:
    if entry[0] in EXCLUDED_DN: continue
    print(get_new_ldif(entry))

#for i in ldif_rec.all_records:
    #passw = i[1].get('userPassword')
    #if not passw: continue
    #if not b'SSHA' in passw[0].upper(): print(i[0], passw)
