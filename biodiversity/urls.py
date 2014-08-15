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
    url(r'search/$', search_results_page),
    url(r'search/ajax/$', search_results),

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
    url(r'^api/classification/$', classification_flare_json),
    url(r'^api/count_family/$', count_family),
    url(r'api/threats/([a-zA-Z|_]+)/(\d+)/$', threats),
    url(r'api/area/$', area_hierarchy),
    url(r'api/iucn/([a-z]+)/$',iucn_classification),
    url(r'api/iucn/([a-z]+)/([a-zA-Z|_]+)/$',iucn_classification),
    url(r'api/pie/([a-z|_]+)/$', piechart_json),
    url(r'api/pie/([a-z|_]+)/([a-zA-Z|_]+)/$', piechart_json),
    url(r'api/stackedbar/([a-z|_]+)/$', stackedbar_json),
    url(r'api/stackedbar/([a-z|_]+)/(\d+)/$', stackedbar_json),
    url(r'api/bar/([a-z|_]+)/(\d+)/$', bar_chart_json),
    url(r'api/zoo_search/([a-zA-Z]+)/$', zoo_search),

    url(r'api/search/([a-z]+)/(.*)$', search),

    url(r'species_list/(\d+)/([a-zA-Z]+)/$', species_list),

    url(r'data_insights/species/variety/$', species_variety),
    url(r'data_insights/species/tree/$', species_tree),
    url(r'data_insights/iucn/([a-z]+)/([a-zA-Z|_]+)/$',iucn_clazz),
    url(r'data_insights/protected_areas/area/([a-z]+)/$',area),
    url(r'data_insights/protected_areas/comparison/(\d+)/(\d+)/$',comparison),
    url(r'data_insights/protected_areas/bar/([a-z]+)/$',bar),
    url(r'data_insights/zoo/species/(\d+)/$',species_profile),



    url(r'^admin/', include(admin.site.urls)),

    url(r'^test/$', test),
)
