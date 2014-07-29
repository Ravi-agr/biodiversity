from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from biodiv.models import *

def species_variety(request):
    return render(request, "analytics/sunburst.html", { 'type':'species_diversity'})

def species_tree(request):
    return render(request, "analytics/taxonomy_tree.html")

def iucn_clazz(request,type, group):
    return render(request, "analytics/hierarchical_bar.html", {'type':type,'group':group})


def area(request, type):
    if type == "pie":
        return render(request, "analytics/sunburst.html", {'type':'area'})
    else:
        return render(request, "analytics/line.html")