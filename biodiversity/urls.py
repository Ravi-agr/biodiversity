from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from biodiv.views.api_views import *
from biodiv.views.renderTemplates import *
from biodiv.views.renderInsights import *


urlpatterns = patterns('',
    # Examples:
    url(r'^$',home),
    url(r'^index.html$',home),
    url(r'^about/$',about),
    url(r'^contact/$',contact),


    url(r'^protected_area/(\d+)/(.*?)/$',protectedArea),
    url(r'^protected_species/$',protectedSpecies),
    url(r'^protected_areas_list/$',protectedAreasList),
    url(r'^data_insights/$',dataInsights),


    url(r'^species/(\d+)/([a-zA-Z|_|-]+)/$', species),

    url(r'^taxa/([a-zA-Z|_|-]+)/([a-zA-Z|_|-]+)/$', loadTaxa),

    url(r'^api/$', api),
    url(r'^api/species/(\d+)/([a-z|_]+)/$', apiSpecies),
    url(r'^api/protected_areas/(\d+)/([a-zA-Z|_|-]+)/$', apiProtected),
    url(r'^api/(count|checklist)/$', apiOthers),
    url(r'^api/(count|checklist)/([a-zA-Z]+)/$', apiOthers),
    url(r'^api/csv/pa/(\d+)/$',csvProtectedChecklist),
    url(r'api/csv/all/([a-zA-Z]+)/$', csvSpeciesChecklist),
    url(r'^api/classification/(\d+)/$', classification_flare_json),
    url(r'^api/count_family/(\d+)/$', count_family),
    url(r'api/threats/([a-zA-Z|_]+)/(\d+)/$', threats),
    url(r'api/area/$', area_hierarchy),
    url(r'api/iucn/([a-z]+)/$',iucn_classification),

    url(r'species_list/(\d+)/([a-zA-Z]+)/$', species_list),

    url(r'data_insights/species/variety/(\d+)/$', species_variety),
    url(r'data_insights/species/tree/(\d+)/$', species_tree),
    url(r'data_insights/protected_areas/area/$',area),


    url(r'^admin/', include(admin.site.urls)),

    url(r'^test/$', test),
)
