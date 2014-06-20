from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from biodiv.views.api_views import *
from biodiv.views.renderTemplates import *


urlpatterns = patterns('',
    # Examples:
    url(r'^$',home),
    url(r'^index.html$',home),

    url(r'^protected_area/(\d+)/(.*?)/$',protectedArea),
    url(r'^protected_species/$',protectedSpecies),
    url(r'^protected_areas_list/$',protectedAreasList),

    url(r'^species/(\d+)/([a-zA-Z|_|-]+)/$', species),

    url(r'^api/$', api),
    url(r'^api/species/(\d+)/([a-z|_]+)/$', apiSpecies),
    url(r'^api/protected_areas/(\d+)/([a-zA-Z|_|-]+)/$', apiProtected),
    url(r'^api/(count|checklist)/$', apiOthers),
    url(r'^api/(count|checklist)/([a-zA-Z]+)/$', apiOthers),
    url(r'^api/csv/pa/(\d+)/$',csvProtectedChecklist),
    url(r'api/csv/all/([a-zA-Z]+)/$', csvSpeciesChecklist),


    url(r'^admin/', include(admin.site.urls)),
)
