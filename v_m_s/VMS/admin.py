from django.contrib import admin
from .models import Asset, Report, VisitorPreRegistration, CustomUser, Visitor

admin.site.register(Asset)
admin.site.register(Report)
admin.site.register(VisitorPreRegistration)
admin.site.register(CustomUser)
admin.site.register(Visitor)
