#!/usr/bin/env python3
import csv
import dateutil.parser

from django.db import transaction
from django.conf import settings
from django.utils import timezone
from pprint import pprint

from .models import Identity

def clean_field(value):
    return value.strip()


@transaction.atomic
def create_accounts_from_csv(csv_file='',
                             test=False,
                             debug=False):
    proc_msg = 'Processing '
    input_file = csv.DictReader(open(csv_file))
    cnt = 0
    for da in input_file:
        if debug:
            print(proc_msg)
            pprint(da)

        # gets identity from email
        email = clean_field(da['email'])
        identity = Identity.objects.filter(email=email)

        if identity:
            identity = identity.first()
            if debug:
                msg = 'INFO: Found already stored identity {} from email {}'
                print(msg.format(identity, email))
        else:
            identity = Identity(
                        name = clean_field(da['first_name']),
                        surname = clean_field(da['last_name']),
                        email = clean_field(da['email']),
                        telephone = clean_field(da['tel']),
                        codice_fiscale = clean_field(da['codice_fiscale']))

            date_of_birth = clean_field(da['date_of_birth'])
            place_of_birth = clean_field(da['place_of_birth'])

            if date_of_birth:
                identity.date_of_birth = clean_field(da['date_of_birth'])
            if place_of_birth:
                identity.place_of_birth = clean_field(da['place_of_birth'])

            if not test:
                identity.save()

        if debug:
            print('identity: {}'.format(identity))

        print('Create Identity for {}'.format(identity))
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
