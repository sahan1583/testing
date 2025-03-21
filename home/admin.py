from django.contrib import admin
from .models import Case
from .models import CaseUpdate

# Register your models here.
admin.site.register(Case)
admin.site.register(CaseUpdate)
