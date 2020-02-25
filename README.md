Django LDAP Identity Manager
----------------------------

Description here

Features:
- here
- and here

# Configure your IdM

Copy `django_idm.settingslocal.py.example` to `django_idm.settingslocal.py` to customize your project.

#### Django form builder

Django IdM uses [django-form-builder](https://github.com/UniversitaDellaCalabria/django-form-builder)
to let you configure the LDAP fields that would be editable by users.
Example, in `settingslocal.py`:

````
DJANGO_FORM_BUILDER_FIELDS = OrderedDict([
     ('mail', ('CustomEmailField', {'label': 'Email',
                                    'required': True,
                                    'help_text': 'name.surname@testunical.it, comunque l\'email utilizzata in fase di registrazione. '}, '')),
     ('telephoneNumber', ('CustomCharField', {'label': 'Telefono',
                                              'required': True,
                                              'help_text': ''}, '')),
     ('cn', ('CustomCharField', {'label': 'Campo data',
                                          'required': True,
                                          'help_text': ''}, '')),
     ('displayName', ('CustomCharField', {'label': 'Campo data',
                                          'required': True,
                                          'help_text': ''}, '')),
 ])
````

#### Requestable Identity

You can let new users to ask a new account.
Edit `settingslocal.py` and point `PROVISONING_REQUEST_ID_APPNAME` to your favourite app, example: 'request_identity'`.
You can create your custom app to handle the identity requests.


# Running tests

````
pip install -r requirements-dev.txt
./manage.py test

# or
./manage.py test --verbosity 1 provisioning.tests

coverage erase
coverage run  manage.py test
coverage report -m
````

# Authors

- Giuseppe De Marco - giuseppe.demarco@unical.it
- Francesco Filicetti - francesco.filicetti@unical.it
