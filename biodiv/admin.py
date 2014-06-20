from django.contrib import admin
from biodiv.models import *

class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('species_id', 'name', 'scientific_name', 'group')

class ProtectedAdmin(admin.ModelAdmin):
    list_display = ('pa_id', 'name', 'designation')

admin.site.register(Species, SpeciesAdmin)
admin.site.register(ProtectedAreas, ProtectedAdmin)