#!/bin/bash

source ~/securedrop-alpha/bin/activate
cd /var/www/django-alpha
./manage.py test --noinput --keepdb
