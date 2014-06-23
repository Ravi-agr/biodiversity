__author__ = 'sawal_000'

from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from biodiv.models import *



def home(request):
    return render(request,'index.html')

def api(request):
    pa = ProtectedAreas.objects.order_by("pa_id")
    grp = Species.objects.values('group').distinct()

    return render(request, 'api.html',{'protected_areas':pa, 'group':grp})

def protectedArea(request,id,name):
    import re
    try:
        pa = ProtectedAreas.objects.get(pa_id = id)
    except ProtectedAreas.DoesNotExist:
        raise Http404
    redir = re.match("Redirect ([0-9]+)",pa.description)
    if redir:
        pa_id = redir.group(1)
        pa = ProtectedAreas.objects.get(pa_id = pa_id)
        pa.name = pa.name.replace(" ","_")
        return HttpResponseRedirect("/protected_area/"+pa_id+"/"+pa.name+"/")

    pa.image = pa.getURL(150)
    if pa.area == int(pa.area):
        pa.area = int(pa.area)


    pa.area = "{:,}".format(pa.area)

    pa.related = pa.getRelated()

    pa.species =  ProtectedAreas.objects.speciesChecklistObj(pa.pa_id)



    return render(request, 'protected_area.html', {'pa':pa})

def protectedAreasList(request):
    pa = ProtectedAreas.objects.all()
    p = {}
    for item in pa:
        if "Buffer" in item.designation: continue
        if not item.designation in p: p[item.designation] = []
        p[item.designation].append(item)


    return render(request, 'protected_areas_list.html', {'pa_list': p})


def protectedSpecies(request):
    from urllib2 import urlopen

    protected = Status.objects.filter(protected = True).select_related().distinct('species_id__name')


    div = 3

    grp_cnt = {"Birds":0, "Mammal":0, "Herpeto":0}
    grp_species = {"Birds":[], "Mammal":[], "Herpeto":[]}
    section = {"Birds":[], "Mammal":[], "Herpeto":[]}
    for i in xrange(len(protected)):
        grp = protected[i].species_id.group
        grp_cnt[grp] +=1

        img = protected[i].species_id.getURL(160)
        cn = protected[i].species_id.getCommonName()
        if not img:
            protected[i].image = "/assets/images/default_thumb.png"
        else:
            protected[i].image = img[0]

        if not cn:
            protected[i].common_name = ""
        else:
            protected[i].common_name = cn[0].common_name.title()


        section[grp].append(protected[i])
        if grp_cnt[grp] % div == 0:
            grp_species[grp].append(section[grp])
            section[grp] = []

    for k in grp_cnt.keys():
        if section[k]:
            grp_species[k].append(section[k])




    return render(request, 'protected_species.html', {'species':grp_species})


def species(request,id,name):

    try:
        s = Species.objects.get(species_id = id)
    except Species.DoesNotExist:
        raise Http404

    img = s.getURL(100)
    names = Names.objects.filter(species_id = id)
    status = Status.objects.filter(species_id = id)
    clazz = Classification.objects.filter(species_id = id)
    iucn = IucnData.objects.filter(species_id = id)
    assessment_history = IucnAssessmentHistory.objects.filter(species_id = id)
    habitat = IucnHabitat.objects.filter(species_id = id)
    conservation = IucnConservation.objects.filter(species_id = id)
    threat = IucnThreat.objects.filter(species_id = id)
    fauna_region = FaunaRegion.objects.filter(species_id = id)
    flora_region = FloraRegion.objects.filter(species_id = id)


    external_keys = ExternalKeys.objects.filter(species_id = id)
    description = Description.objects.filter(species_id = id).distinct('type')
    description_titles = ["abstract", "biology and behaviour", "characteristics and evolution", "conservation","threats","habitat"]
    common = CommonNames.objects.filter(species_id = id)

    p = SpeciesPa.objects.filter(species_id = id).select_related()
    pa = []
    for item in p:
        pa.append(item.pa_id)

    sp = {'main': s,
          'name':names,
          'img':img,
          'clazz':clazz,
          'status':status,
          'iucn':iucn,
          'assessment_history':assessment_history,
          'habitat':habitat,
          'conservation':conservation,
          'threats':threat,
          'fauna_region':fauna_region,
          'flora_region':flora_region,
          'external_keys':external_keys,
          'description':description,
          'titles':description_titles,
          'common':common,
          'pa':pa}

    print img
    return render(request, 'species.html', sp)






