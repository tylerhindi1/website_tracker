from django.contrib import admin
from .models import UserLocation, TokenSummary, VisitCount
# Register your models here.

admin.site.register(UserLocation)
admin.site.register(TokenSummary)
admin.site.register(VisitCount)
