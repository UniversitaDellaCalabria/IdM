#!/usr/bin/env python3
import csv
import dateutil.parser
import logging

from django.db import transaction
from django.conf import settings
from django.utils import timezone
from pprint import pprint

from .models import Identity

def clean_field(value):
    return value.strip()

logger = logging.getLogger(__name__)


@transaction.atomic
def create_accounts_from_csv(csv_file='',
                             test=False,
                             debug=False):
    proc_msg = 'Processing: '
    input_file = csv.DictReader(open(csv_file))
    cnt = 0
    for da in input_file:
        logger.debug(proc_msg+str(da))

        # gets identity from email
        mail = clean_field(da['mail'])
        identity = Identity.objects.filter(mail=mail)

        if identity:
            identity = identity.first()
            msg = 'INFO: Found already stored identity {} from email {}'
            logger.debug(msg.format(identity, mail))
        else:
            identity = Identity(
                        name = clean_field(da['first_name']),
                        surname = clean_field(da['last_name']),
                        email = clean_field(da['mail']),
                        telephoneNumber = clean_field(da['tel']),
                        codice_fiscale = clean_field(da['codice_fiscale']))

            date_of_birth = clean_field(da['date_of_birth'])
            place_of_birth = clean_field(da['place_of_birth'])

            if date_of_birth:
                identity.date_of_birth = clean_field(da['date_of_birth'])
            if place_of_birth:
                identity.place_of_birth = clean_field(da['place_of_birth'])

            if not test:
                identity.save()

        logger.debug('identity: {}'.format(identity))
        logger.info('Create Identity for {}'.format(identity))
        cnt += 1
    return cnt


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-csv', required=True,
                        help="csv file to import")
    parser.add_argument('-test', required=False, action="store_true",
                        help="do not save imports, just test")
    parser.add_argument('-debug', required=False, action="store_true",
                        help="see debug message")
    args = parser.parse_args()

    create_accounts_from_csv(csv_file=args.csv,
                             test=args.test,
                             debug=args.debug)
