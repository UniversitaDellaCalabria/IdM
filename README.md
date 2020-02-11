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
