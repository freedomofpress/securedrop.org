#!/bin/bash

source ~/securedrop/bin/activate
cd /var/www/django/
./manage.py test --noinput --keepdb
