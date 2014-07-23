from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from biodiv.models import *

def species_variety(request, pa_id):
    return render(request, "analytics/sunburst.html", {'pa_id':pa_id, 'type':'species_diversity'})

def species_tree(request, pa_id):
    return render(request, "analytics/taxonomy_tree.html", {'pa_id':pa_id})

def area(request):
    return render(request, "analytics/sunburst.html", {'type':'area'})