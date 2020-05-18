from django.conf import settings
from ldap_peoples.models import *

settings.LDAP_SEARCH_LIMIT = None
peoples = LdapAcademiaUser.objects.all()

nocf = []
nocode = []
fixedcode = []
failed_cf_dip = []
for i in peoples:
    if not getattr(i, 'schacPersonalUniqueCode', None):
        nocode.append(i.uid)
        if i.uid.isdigit():
            try:
                i.schacPersonalUniqueCode = ['urn:schac:personalUniqueCode:IT:unical.it:dipendente:{}'.format(i.uid)]
                i.save()
            except Exception as e:
                import pdb; pdb.set_trace()
            fixedcode.append(i.uid)
        else:
            nocode.append(i.uid)
    if not i.schacPersonalUniqueID or len(i.schacPersonalUniqueID[0]) < 42:
        if 'dipendente' in i.schacPersonalUniqueCode[0]:
            #  try:
                #  i.schacPersonalUniqueID = ['urn:schac:personalUniqueID:IT:CF:{}'.format(cf_dip[int(i.uid)])]
                #  i.save()
            #  except Exception as e:
                #  print(e, i)
                #  failed_cf_dip.append(i)
            nocf.append((i.uid, getattr(i, 'schacPersonalUniqueCode', []), i.schacPersonalUniqueID))
        elif 'studente' in i.schacPersonalUniqueCode[0]:
            i.schacPersonalUniqueID = ['urn:schac:personalUniqueID:IT:CF:{}'.format(i.uid)]
            i.save()
            continue
        else:
            nocf.append((i.uid, getattr(i, 'schacPersonalUniqueCode', []), i.schacPersonalUniqueID))




"""
SELECT MATRICOLA, COD_FIS from   (
select a.matricola, a.cognome, a.nome, a.cod_fis, dt_nascita, id_comu_nasc, ds_comune_nasc, ds_prov_nasc, id_nazione_nasc, ds_nazi_nasc,
id_comu_res, ds_comune_res, cd_cap_res, indirizzo_res, num_civico_res, email, DT_RAP_INI, DT_RAP_FIN
from V_IE_RU_PERSONALE@LNK_CSA a
UNION
SELECT a.matricola, a.cognome, a.nome, a.cod_fis, dt_nascita, id_comu_nasc, ds_comune_nasc, ds_prov_nasc, id_nazione_nasc, ds_nazi_nasc,
id_comu_res, ds_comune_res, cd_cap_res, indirizzo_res, num_civico_res, email, DT_RAP_INI, DT_RAP_FIN
FROM V_IE_RU_PERSONALE_CESSATO@LNK_CSA a
) WHERE
MATRICOLA IN (...);
"""
