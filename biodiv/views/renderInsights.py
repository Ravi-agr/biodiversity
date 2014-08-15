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

def comparison(request, id1, id2):
    pa1 = ProtectedAreas.objects.get(pa_id = id1)
    pa2 = ProtectedAreas.objects.get(pa_id = id2)
    return render(request, "analytics/comparison.html", {'pa1':pa1, 'pa2':pa2})

def bar(request, type):
    if type == "iucn":
        return render(request, "analytics/stacked.html")
    else:
        return render(request, "analytics/bar.html", {"type": type})

def species_profile(request,id):
    species = Zoo.objects.get(id = id)
    return render(request, "analytics/zoo_species.html", {"species":species, 'total':species.male + species.female + species.unknown})

