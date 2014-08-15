from django.db.models.query_utils import Q
from requests.exceptions import ConnectionError
from wikipedia.exceptions import *

__author__ = 'sawal_000'

from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from biodiv.models import *


def home(request):
    return render(request,'index.html')

def about(request):
    return render(request, 'about.html')
def contact(request):
    return render(request, 'contact.html')

def test(request):
    return render(request, 'd3_test.html')

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

    pa.image = pa.getURL(600)
    if pa.area == int(pa.area):
        pa.area = int(pa.area)


    pa.area = "{:,}".format(pa.area)

    pa.related = pa.getRelated()

    pa.species =  ProtectedAreas.objects.speciesChecklistObj(pa.pa_id)

    type = ["Mammal", "Birds", "Herpeto", "Fish", "Phanerogams", "Pteridophytes"]

    return render(request, 'protected_area.html', {'pa':pa, 'type':type})

def protectedAreasList(request):
    pa = ProtectedAreas.objects.all()
    p = {}
    for item in pa:
        if "Buffer" in item.designation: continue
        if not item.designation in p: p[item.designation] = []
        p[item.designation].append(item)

    type = ["National Park", "Conservation Area", "Wildlife Reserve",  "Hunting Reserve", "Ramsar Site", "World Heritage Site"]
    return render(request, 'protected_areas_list.html', {'pa_list': p, 'pa_type':type, 'fact':random_fact()})


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

    img = s.getURL(400)
    img_org = s.getURL()

    import urllib2



    for i in range(len(img)):
        try:
            urllib2.urlopen(img[i])
        except urllib2.HTTPError, e:
            img[i] = img_org[i]
        except urllib2.URLError:
            img[i] = ""


    names = Names.objects.filter(species_id = id)
    status = Status.objects.filter(species_id = id)
    clazz = Classification.objects.filter(species_id = id)
    iucn = IucnData.objects.filter(species_id = id)
    assessment_history = IucnAssessmentHistory.objects.filter(species_id = id)
    habitat = IucnHabitat.objects.filter(species_id = id, suitability = " Suitable").order_by("habitat_number").distinct("habitat_number")
    conservation = IucnConservation.objects.filter(species_id = id)
    threat = IucnThreat.objects.filter(species_id = id)
    fauna_region = FaunaRegion.objects.filter(species_id = id)
    flora_region = FloraRegion.objects.filter(species_id = id)


    external_keys = ExternalKeys.objects.filter(species_id = id)
    description = Description.objects.filter(species_id = id).exclude(type = "abstract").distinct('type')
    description_titles = ["biology", "characteristics", "conservation","threats","habitat","description","uses","distribution and habitat","behaviour","behaviour and ecology","habits","reproduction","behavior","medicinal uses","diet","medicinal uses"]
    abstract = Description.objects.filter(species_id = id, type__iexact = "abstract")
    if abstract:
        abstract = abstract[0]
    common = CommonNames.objects.filter(species_id = id)

    p = SpeciesPa.objects.filter(species_id = id).select_related()
    pa = []
    for item in p:
        pa.append(item.pa_id)

    nrdb = ""
    if status:
        if status[0].nrdb == "EXN": nrdb = "Extinct in Nepal"
        elif status[0].nrdb == "C": nrdb = "Critically Endangered"
        elif status[0].nrdb == "E": nrdb = "Endangered"
        elif status[0].nrdb == "V": nrdb = "Vulnerable"
        elif status[0].nrdb == "S": nrdb = "Susceptible"
        elif status[0].nrdb == "I": nrdb = "Introduced"
        elif status[0].nrdb == "UR": nrdb = "Under Recorded (BPP)"

    filtered_description = []
    for item in description:
        if item.type in description_titles:
            filtered_description.append(item)

    import json
    iucn_clazz = json.load(open("iucn.json"))
    iucn_classification = {}

    habitat_list = []
    for item in habitat:
        n = item.habitat_number
        if not n.isdigit(): n = n[:-1]

        a = []
        while not n.isdigit():
            a.insert(0,iucn_clazz["habitat"][n])
            n = n.rsplit(".",1)[0]
        a.insert(0,iucn_clazz["habitat"][n])

        habitat_list.append(a)

    d = {}
    for item in habitat_list:
        if not item[0] in d: d[item[0]] = []
        for i in range(len(item)):
            if i == 1 :
                d[item[0]].append(item[1])
            elif i > 1:
                d[item[0]][len(d[item[0]])-1] += " > " + item[i]

    iucn_classification["habitat"] = d

    threat_list = []
    for item in threat:
        n = item.threat_number
        if not n.isdigit(): n = n[:-1]

        a = []
        while not n.isdigit():
            a.insert(0,iucn_clazz["threat"][n])
            n = n.rsplit(".",1)[0]
        a.insert(0,iucn_clazz["threat"][n])

        threat_list.append(a)

    d = {}
    for item in threat_list:
        if not item[0] in d: d[item[0]] = []
        for i in range(len(item)):
            if i == 1 :
                d[item[0]].append(item[1])
            elif i > 1:
                d[item[0]][len(d[item[0]])-1] += " > " + item[i]

    iucn_classification["threat"] = d

    conservation_list = []
    for item in conservation:
        n = item.conservation_number
        if not n.isdigit(): n = n[:-1]

        a = []
        while not n.isdigit():
            a.insert(0,iucn_clazz["conservation"][n])
            n = n.rsplit(".",1)[0]
        a.insert(0,iucn_clazz["conservation"][n])

        conservation_list.append(a)

    d = {}
    for item in conservation_list:
        if not item[0] in d: d[item[0]] = []
        for i in range(len(item)):
            if i == 1 :
                d[item[0]].append(item[1])
            elif i > 1:
                d[item[0]][len(d[item[0]])-1] += " > " + item[i]

    iucn_classification["conservation"] = d

    types = ['kingdom', 'phylum', 'class_field', 'order', 'family', 'genus']
    related = []

    if clazz:
        for item in reversed(types):
            x = Classification.objects.filter(**{item: getattr(clazz[0],item)}).exclude(species_id__species_id = id).select_related()
            for a in x:
                if not a.species_id in related:
                    related.append(a.species_id)
                if len(related) > 5: break
            if len(related) > 5: break

    sp = {'main': s,
          'name':names,
          'img':img,
          'clazz':clazz,
          'status':status,
          'nrdb':nrdb,
          'iucn':iucn,
          'assessment_history':assessment_history,
          'habitat':iucn_classification["habitat"],
          'conservation':iucn_classification["conservation"],
          'threats':iucn_classification["threat"],
          'fauna_region':fauna_region,
          'flora_region':flora_region,
          'external_keys':external_keys,
          'description':filtered_description,
          'titles':description_titles,
          'abstract':abstract,
          'common':common,
          'pa':pa,
          'related': related}


    return render(request, 'species.html', sp)

def loadTaxa(request, type, keyword):

    import wikipedia


    try:
        description = wikipedia.summary(keyword, sentences = 10)
    except PageError:
        description = ""
    except ConnectionError:
        description = ""
        
    clazz = Classification.objects.filter(**{type+'__iexact': keyword}).select_related()[:25]

    species = []
    speices_with_img = Images.objects.all().values_list('species_id', flat = True).distinct()

    for item in clazz:
        if item.species_id.species_id in speices_with_img:
            species.append(item.species_id)
    for item in clazz:
        if not item.species_id.species_id in speices_with_img:
            species.append(item.species_id)


    if type.lower() == "class_field": type = "Class"

    return render(request, 'taxa.html', {'type': type, 'keyword': keyword, 'description': description, 'species':species})


def dataInsights(request):
    pa_with_species = SpeciesPa.objects.values_list('pa_id', flat = True).distinct()
    pa = ProtectedAreas.objects.filter(pa_id__in = pa_with_species).order_by("pa_id")
    grp = Species.objects.values('group').distinct()

    return render(request, 'data_insights.html', {'pa':pa, 'group':grp})

def species_list(request, id, type):

    try:
        pa = ProtectedAreas.objects.get(pa_id = id)
    except ProtectedAreas.DoesNotExist:
        raise Http404


    pa.species =  ProtectedAreas.objects.speciesChecklistObj(pa.pa_id)

    return render(request, 'species_list.html', {'pa':pa, 'group':type})

def random_fact():
    f = open("facts.txt","r")
    facts = f.readlines()
    from random import randrange
    return facts[randrange(len(facts))]


def search_results_page(request):
    keyword = ""
    pa_with_species = SpeciesPa.objects.values_list('pa_id', flat = True).distinct()
    pa = ProtectedAreas.objects.filter(pa_id__in = pa_with_species).order_by("pa_id")

    if 'q' in request.GET:
        keyword = request.GET['q']

    return render(request, 'search_results_page.html', {'keyword':keyword, 'pa':pa})

def search_results(request):
    from haystack.query import SearchQuerySet
    from api_views import ValuesQuerySetToDict

    result_iucn = None
    result_pa = None
    if request.GET['iucn'] != "Any":
        result_iucn = IucnData.objects.filter(status = request.GET['iucn']).values_list("species_id", flat=True)

    if request.GET['pa'] != "Any":
        result_pa = SpeciesPa.objects.filter(pa_id = request.GET['pa']).values_list("species_id", flat=True)

    kwargs = {}
    if request.GET['cites'] != "Any": kwargs['cites'] = request.GET['cites']
    if request.GET['nrdb'] != "Any": kwargs['nrdb'] = request.GET['nrdb']
    if request.GET.get('protected', False) != "Any": kwargs['protected'] = request.GET.get('protected', False) == "True"

    result_status = Status.objects.filter(**kwargs).values_list("species_id", flat=True)
    all = Species.objects.all().values_list("species_id", flat=True)
    if 'keyword' in request.GET:
#        sqs = SearchQuerySet().filter(content = request.GET['keyword'])
#        related = []
#        for x in sqs:
#            o = x.object.species_id
#            if type(o) is int:
#                related.append(o)
#            else:
#                related.append(o.species_id)

        related = ValuesQuerySetToDict(CommonNames.objects.filter(common_name__iregex=r"\y{0}\y".format(request.GET['keyword'])).values_list('species_id__species_id', flat=True))
        related += ValuesQuerySetToDict(Species.objects.filter(name__iregex=r"\y{0}\y".format(request.GET['keyword'])).values_list('species_id', flat=True))
        related += ValuesQuerySetToDict(Names.objects.filter(synonym__iregex=r"\y{0}\y".format(request.GET['keyword'])).values_list('species_id__species_id', flat=True))

        filter_by = {'species_id__in':set(related)}
    else:
        filter_by = {'species_id__in':set(all)}

    if kwargs:
        filter_by['species_id__in'] &= set(result_status)
    if result_iucn:
        filter_by['species_id__in'] &= set(result_iucn)

    if request.GET.get('type',False) != "Any":
        filter_by['group'] = str(request.GET.get('type',False))

    if result_pa:
        filter_by['species_id__in'] &= set(result_pa)


    if len(filter_by['species_id__in']) == len(all):
        del filter_by['species_id__in']
    else:
        filter_by['species_id__in'] = list(filter_by['species_id__in'])

    pg = 1
    if 'pg' in request.GET: pg = int(request.GET['pg'])


    result = Species.objects.filter(**filter_by).order_by('group','name')

    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(result,10)
    try:
        pages = paginator.page(pg)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)

    print request.get_full_path().rsplit('&',1)[0]

    return render(request, 'search_results.html', {'pages':pages, 'path':request.get_full_path().rsplit('&',1)[0]})

