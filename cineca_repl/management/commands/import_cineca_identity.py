import datetime
import json

from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand, CommandError
from identity.models import (Identity,
                             IdentityExtendendStatus,
                             AdditionalAffiliation)
from provisioning.utils import get_date_from_string
from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc


def fix_matricola(value):
    if isinstance(value, int):
        value = str(value)
    return value.zfill(6)

def clean_matricola(value):
    return value.lstrip('0')

def fix_date_of_birth(value):
    return get_date_from_string(value)

def get_affiliations(value_dict):
    """
    value = the tuple dictionary
    gruppo
    matricola_dipendente
    matricola_studente
    """
    pass

def get_guys(update = False):
    engine = create_engine(settings.CINECA_DB_URL)
    metadata = MetaData()
    identita_digitale = Table('TB_IDENTITA_DIGITALI', metadata,
                              autoload=True, autoload_with=engine,
                              oracle_resolve_synonyms=True)
    session = Session(engine)
    gruppo = identita_digitale.columns.get('gruppo')
    matricola_studente = identita_digitale.columns.get('matricola_studente')
    table_query = session.query(identita_digitale)
    valid = table_query.filter(~gruppo.contains('legacy')).order_by(matricola_studente)

    user = get_user_model().objects.filter(is_superuser=True).first()
    cnt = 0
    failed = []
    for guy in valid:
        print('.', end='')
        if not guy.email:
            failed.append(guy)
            continue

        identity = Identity.objects.filter(email=guy.email,
                                           tin=guy.tin).first()
        if identity and update:
            # get it and update
            identity.name = guy.nome
            identity.surname = guy.cognome
            identity.place_of_birth = guy.comune_nascita
            identity.date_of_birth = fix_date_of_birth(guy.data_nascita)
            identity.save()
            identity.additional_affiliations_set.all().delete()
            LogEntry.objects.log_action(
                user_id         = user.pk,
                content_type_id = ContentType.objects.get_for_model(identity).pk,
                object_id       = identity.pk,
                object_repr     = identity.__str__(),
                action_flag     = CHANGE,
                change_message  = 'Aggiornato con import_cineca_identity')
        elif identity:
            # get it and continue, do not update
            continue
        else:
            guy_repr = json.dumps(guy._asdict())
            identity = Identity.objects.create(name = guy.nome,
                                               surname = guy.cognome,
                                               place_of_birth = guy.comune_nascita,
                                               date_of_birth = fix_date_of_birth(guy.data_nascita),
                                               tin = guy.tin,
                                               mail = guy.mail,
                                               flusso = 'import',
                                               descrizione_flusso = guy_repr)
            LogEntry.objects.log_action(
                user_id         = user.pk,
                content_type_id = ContentType.objects.get_for_model(identity).pk,
                object_id       = identity.pk,
                object_repr     = identity.__str__(),
                action_flag     = ADDITION,
                change_message  = 'Importato con import_cineca_identity')
        # if something goes wrong:
        try:
            d = dict(identity = identity)
            if guy.matricola_studente:
                d['name'] = 'student'
                d['unique_code'] = clean_matricola(guy.matricola_studente)
                aff = AdditionalAffiliation.objects.filter(**d)
                if not aff:
                    AdditionalAffiliation.objects.create(**d)

            if guy.matricola_dipendente:
                d['name'] = 'employee'
                d['unique_code'] = clean_matricola(guy.matricola_dipendente)
                aff = AdditionalAffiliation.objects.filter(**d)
                if not aff:
                    AdditionalAffiliation.objects.create(**d)
                identity.affiliation = 'dipendente'
                identity.save()

            cnt += 1
        except Exception as e:
            print(e)
            identity.delete()
            failed.append(guy)
        print(guy)
    return {'imported': cnt, 'failed': failed}


class Command(BaseCommand):
    help = 'Import CINECA Identity'

    def add_arguments(self, parser):
        parser.add_argument('-debug', required=False,
                            default=True, action="store_true")
        parser.add_argument('-email', required=False,
                            action="store_true",
                            help="Invia una email in caso di errori")

    def handle(self, *args, **options):
        print(self.help)
        imported = get_guys()
        failed = imported['failed']
        if failed:
            error_msg = 'Errors on %d guys' % len(failed)
            self.stdout.write(self.style.ERROR(error_msg))
            if options.get('debug'):
                for i in failed:
                    print('Failed:', i)
            if options.get('email'):
                mail_admins('Import CSA Identity:  {}'.format(error_msg),
                            '\n'.join(i for i in failed))
