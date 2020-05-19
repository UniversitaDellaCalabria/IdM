failed2 = [] # 1241,
#cnt = 100000
cnt = 0
for pe in failed:
    #print(cnt, pe)
    #  if pe.schacPersonalUniqueID:
        #  l = []
        #  print('{} uniqueID'.format(pe))
        #  for i in pe.schacPersonalUniqueID:
            #  spl = i.split(':')
            #  n = ':'.join((spl[0], spl[1], spl[2], spl[3].lower(), spl[4].upper(), spl[5].lower()))
            #  l.append(n)
        #  if pe.schacPersonalUniqueID != l:
            #  pe.schacPersonalUniqueID = l
        #  try:
            #  pe.save()
        #  except:
            #  other = LdapAcademiaUser.objects.get(schacPersonalUniqueID=n)
            #  if other.cn == pe.cn and pe.uid.isdigit():
                #  print('Deleting {} schacPersonalUniqueID'.format(other))
                #  other.schacPersonalUniqueID = []
                #  other.save()
                #  pe.save()

    #  if pe.schacPersonalUniqueCode:
        #  print('{} uniqueCode'.format(pe))
        #  l = []
        #  for i in pe.schacPersonalUniqueCode:
            #  l.append(i.replace('IT:', 'it:'))
        #  if pe.schacPersonalUniqueCode != l:
            #  pe.schacPersonalUniqueCode = l
        #  try:
            #  pe.save()
        #  except:
            #  other = LdapAcademiaUser.objects.get(schacPersonalUniqueCode=l[0])
            import pdb; pdb.set_trace()
            #  failed2.append(pe)
    if pe.schacHomeOrganizationType:
        print('{} HomeOrgType'.format(pe))
        l = []
        for i in pe.schacHomeOrganizationType:
            l.append(i.replace('IT:', 'it:'))
        if pe.schacHomeOrganizationType != l:
            pe.schacHomeOrganizationType = l
        pe.save()
    cnt += 1


codes = []
ids = []
typeorg = []
for pe in peoples:
    for ele in pe.schacPersonalUniqueCode:
        if ':IT:' in ele:
            codes.append(pe)
    for ele in pe.schacPersonalUniqueID:
        if ':IT:' in ele:
            ids.append(pe)
    #  for ele in pe.schacHomeOrganizationType:
        #  if ':IT:' in ele:
            #  typeorg.append(pe)

for pe in typeorg:
    if pe.schacHomeOrganizationType:
        print('{} HomeOrgType'.format(pe))
        l = []
        for i in pe.schacHomeOrganizationType:
            l.append(i.replace('IT:', 'it:'))
        if pe.schacHomeOrganizationType != l:
            pe.schacHomeOrganizationType = l
            pe.save()

for pe in ids:
    if pe.schacPersonalUniqueID:
        l = []
        #  print('{} uniqueID'.format(pe))
        for i in pe.schacPersonalUniqueID:
            if ':it:' in i: continue
            spl = i.split(':')
            n = ':'.join((spl[0], spl[1], spl[2], spl[3].lower(), spl[4].upper(), spl[5].lower()))
            l.append(n)
        if pe.schacPersonalUniqueID != l:
            pe.schacPersonalUniqueID = l
        try:
            pe.save()
        except:
            other = LdapAcademiaUser.objects.get(schacPersonalUniqueID=n)
            if other.uid == pe.uid: continue
            if pe.uid.isdigit():
                print('Deleting {} schacPersonalUniqueID'.format(other))
                other.schacPersonalUniqueID = []
                other.save()
                pe.save()


for pe in codes:
    if pe.schacPersonalUniqueCode:
        l = []
        #  print('{} schacPersonalUniqueCode'.format(pe))
        for i in pe.schacPersonalUniqueCode:
            if ':it:' in i: continue
            print(pe)
            n = i.replace('IT:', 'it:')
            l.append(n)
        if pe.schacPersonalUniqueCode != l:
            pe.schacPersonalUniqueCode = l
        try:
            pe.save()
        except:
            other = LdapAcademiaUser.objects.filter(schacPersonalUniqueCode=n).first()
            if not other: continue
            if other.uid == pe.uid: continue
            if pe.uid.isdigit():
                print('Deleting {} schacPersonalUniqueCode'.format(other))
                other.schacPersonalUniqueCode = []
                other.save()
                pe.save()
            #  else:
                #  print('Removing {} code'.format(pe))
                #  pe.schacPersonalUniqueCode = None
                #  pe.save()


missing_cf = []
missing_code = []
for i in peoples:
    if not getattr(i, 'schacPersonalUniqueCode', None):
        missing_code.append(i)
    if not getattr(i, 'schacPersonalUniqueID', None):
        #print(i.uid, i.schacPersonalUniqueCode, i.schacPersonalUniqueID)
        missing_cf.append(i)
