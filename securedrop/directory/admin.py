from django.contrib import admin

from directory.models import Securedrop


admin.site.site_header = 'SecureDrop'
admin.site.index_title = ''

admin.site.register(Securedrop)
