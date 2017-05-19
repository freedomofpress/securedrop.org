from django.contrib import admin

from directory.models import Securedrop, Result


admin.site.site_header = 'SecureDrop'
admin.site.index_title = ''

admin.site.register(Securedrop)
admin.site.register(Result)
