from __future__ import unicode_literals

from django.db import models, connection
import re


class SpeciesManager(models.Manager):
    def speciesCount(self, group = "all"):
        cursor = connection.cursor()

        if group == "all":
            cursor.execute( """
                        SELECT "Group",COUNT(*) AS "c"  FROM  (SELECT DISTINCT "Name", "Group" FROM "Species") AS "s" GROUP BY "Group";
                        """)
        else:
            cursor.execute( """
                                SELECT "Family",COUNT(*) AS "c"
                                FROM  "Species" "s" INNER JOIN "Classification" "l"
                                ON "s"."Species ID" = "l"."Species ID"
                                WHERE "Group" = %s
                                GROUP BY "Family" ;
                            """,[group])



        data = dict(cursor.fetchall())
        return data


    def speciesChecklist(self, group = "all"):


        if group == "all":
            species = Species.objects.all();

            data = {}
            for item in species:
                if not item.group in data:
                    data[item.group] = []
                data[item.group].append({"species_id":item.species_id, "name":item.name})

        else:

            cursor = connection.cursor();
            cursor.execute( """
                                SELECT "Family","s"."Species ID", "Name"
                                FROM  "Species" "s" INNER JOIN "Classification" "c"
                                ON "s"."Species ID" = "c"."Species ID"
                                WHERE "Group" = %s;

                            """, [group])
            species = cursor.fetchall()
            data = {}
            for item in species:
                if not item[0] in data:
                    data[item[0]] = []
                data[item[0]].append({"species_id":item[1], "name":item[2]});

        return data

class Species(models.Model):
    species_id = models.IntegerField(db_column='Species ID', primary_key=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    name = models.CharField(db_column='Name', max_length=100) # Field name made lowercase.
    scientific_name = models.CharField(db_column='Scientific Name', max_length=200, blank=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    group = models.CharField(db_column='Group', max_length=50, blank=True) # Field name made lowercase.
    correct = models.NullBooleanField(db_column='Correct') # Field name made lowercase.



    objects = SpeciesManager()
    class Meta:
        managed = False
        db_table = 'Species'

    def getURL(self,resolution = None):
        img = Images.objects.getURL(self.species_id, resolution)
        return img

    def getCommonName(self):
        return CommonNames.objects.filter(species_id=self.species_id)


    def getAbstract(self):
        des = Description.objects.filter(species_id=self.species_id, type="abstract")
        if des:
            return des[0].description
        else:
            return None


class ProtectedAreasManager(models.Manager):
    def speciesCount(self, id):
        cursor = connection.cursor()
        cursor.execute( """
                        SELECT "Group",COUNT(*) AS "c"
                        FROM "Species PA" AS "p"
                        INNER JOIN "Species" AS "s" ON "p"."Species ID" = "s"."Species ID"
                        WHERE "p"."PA ID" = %s
                        GROUP BY "Group";
                        """, [id])
        data = dict(cursor.fetchall())
        return data

    def speciesChecklist(self,id):
        cursor = connection.cursor()
        cursor.execute( """
                        SELECT "s"."Species ID","Name","Group"
                        FROM "Species PA" AS "p"
                        INNER JOIN "Species" AS "s" ON "p"."Species ID" = "s"."Species ID"
                        WHERE "p"."PA ID" = %s
                        """, [id])
        data = {"Mammal":[], "Birds":[], "Herpeto":[], "Fish":[], "Phanerogams":[], "Pteridophytes":[], "Bryophytes":[]}

        for row in cursor.fetchall():
            data[row[2]].append({"species_id":row[0], "name":row[1]})
        return data

    def speciesChecklistObj(self,id):

        species = SpeciesPa.objects.filter(pa_id = id).select_related().order_by('?')
        speices_with_img = Images.objects.all().values_list('species_id', flat = True).distinct()

        data = {}
        for item in species:
            s = item.species_id
            if not s.species_id in speices_with_img:
                continue
            if not s.group in data:
                data[s.group] = []
            data[s.group].append(s);

        for item in species:
            s = item.species_id
            if s.species_id in speices_with_img:
                continue
            if not s.group in data:
                data[s.group] = []
            data[s.group].append(s);

        return data


class ProtectedAreas(models.Model):
    pa_id = models.IntegerField(db_column='PA ID', primary_key=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    name = models.CharField(db_column='Name', max_length=150) # Field name made lowercase.
    designation = models.CharField(db_column='Designation', max_length=100) # Field name made lowercase.
    wpda = models.IntegerField(db_column='WPDA', blank=True, null=True) # Field name made lowercase.
    estd_year = models.IntegerField(db_column='Estd year', blank=True, null=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    iucn_category = models.CharField(db_column='IUCN Category', max_length=30, blank=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    area = models.FloatField(db_column='Area', blank=True, null=True) # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True) # Field name made lowercase.
    latitude = models.FloatField(db_column='Latitude', blank=True, null=True) # Field name made lowercase.
    longitude = models.FloatField(db_column='Longitude', blank=True, null=True) # Field name made lowercase.

    objects = ProtectedAreasManager()


    def getURL(self,resolution):
        p = PaImages.objects.getURL(self.pa_id,resolution)
        return p

    def getRelated(self):

        p = ProtectedAreas.objects.filter(name = self.name)

        if len(p) == 1: return None

        if p[0].pa_id == self.pa_id: pa = p[1]
        if p[1].pa_id == self.pa_id: pa = p[0]

        redir = re.match("Redirect ([0-9]+)",pa.description)
        if not redir: return None

        id = redir.group(1)
        if int(id) != self.pa_id: return None

        return pa



    class Meta:
        managed = False
        db_table = 'Protected Areas'



class Citations(models.Model):
    class Meta:
        managed = False
        db_table = 'Citations'

class Classification(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID', primary_key=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    kingdom = models.CharField(db_column='Kingdom', max_length=50, blank=True) # Field name made lowercase.
    phylum = models.CharField(db_column='Phylum', max_length=50, blank=True) # Field name made lowercase.
    class_field = models.CharField(db_column='Class', max_length=50, blank=True) # Field name made lowercase. Field renamed because it was a Python reserved word.
    order = models.CharField(db_column='Order', max_length=50, blank=True) # Field name made lowercase.
    family = models.CharField(db_column='Family', max_length=50, blank=True) # Field name made lowercase.
    genus = models.CharField(db_column='Genus', max_length=50, blank=True) # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Classification'

class CommonNames(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID') # Field name made lowercase. Field renamed to remove unsuitable characters.
    common_name = models.CharField(db_column='Common Name', max_length=255) # Field name made lowercase. Field renamed to remove unsuitable characters.
    class Meta:
        managed = False
        db_table = 'Common Names'

class Description(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID') # Field name made lowercase. Field renamed to remove unsuitable characters.
    type = models.CharField(db_column='Type', max_length=255) # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'Description'

class ExternalKeys(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID', primary_key=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    gbif_key = models.IntegerField(db_column='GBIF Key', blank=True, null=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    iucn_key = models.IntegerField(db_column='IUCN Key', blank=True, null=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    col_key = models.IntegerField(db_column='CoL Key', blank=True, null=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    wikipedia_link = models.CharField(db_column='Wikipedia Link', max_length=255, blank=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    class Meta:
        managed = False
        db_table = 'External Keys'

class FaunaRegion(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID', primary_key=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    ts_wp = models.NullBooleanField(db_column='TS_WP') # Field name made lowercase.
    ts_cp = models.NullBooleanField(db_column='TS_CP') # Field name made lowercase.
    ts_ep = models.NullBooleanField(db_column='TS_EP') # Field name made lowercase.
    mh_wp = models.NullBooleanField(db_column='MH_WP') # Field name made lowercase.
    mh_cp = models.NullBooleanField(db_column='MH_CP') # Field name made lowercase.
    mh_ep = models.NullBooleanField(db_column='MH_EP') # Field name made lowercase.
    hl_wp = models.NullBooleanField(db_column='HL_WP') # Field name made lowercase.
    hl_cp = models.NullBooleanField(db_column='HL_CP') # Field name made lowercase.
    hl_ep = models.NullBooleanField(db_column='HL_EP') # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'Fauna Region'

class FloraRegion(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID', primary_key=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    wp = models.NullBooleanField(db_column='WP') # Field name made lowercase.
    cp = models.NullBooleanField(db_column='CP') # Field name made lowercase.
    ep = models.NullBooleanField(db_column='EP') # Field name made lowercase.
    ts = models.NullBooleanField(db_column='TS') # Field name made lowercase.
    mh = models.NullBooleanField(db_column='MH') # Field name made lowercase.
    hm = models.NullBooleanField(db_column='HM') # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'Flora Region'

class IucnAssessmentHistory(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID') # Field name made lowercase. Field renamed to remove unsuitable characters.
    iucn_key = models.IntegerField(db_column='IUCN Key') # Field name made lowercase. Field renamed to remove unsuitable characters.
    year = models.IntegerField(db_column='Year') # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, blank=True) # Field name made lowercase.
    citation = models.CharField(db_column='Citation', max_length=255, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'IUCN Assessment History'

class IucnConservation(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID') # Field name made lowercase. Field renamed to remove unsuitable characters.
    iucn_key = models.IntegerField(db_column='IUCN Key') # Field name made lowercase. Field renamed to remove unsuitable characters.
    conservation_number = models.CharField(db_column='Conservation Number', max_length=50) # Field name made lowercase. Field renamed to remove unsuitable characters.
    class Meta:
        managed = False
        db_table = 'IUCN Conservation'

class IucnData(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID') # Field name made lowercase. Field renamed to remove unsuitable characters.
    iucn_key = models.IntegerField(db_column='IUCN Key') # Field name made lowercase. Field renamed to remove unsuitable characters.
    status = models.CharField(db_column='Status', max_length=50, blank=True) # Field name made lowercase.
    population_trend = models.CharField(db_column='Population Trend', max_length=50, blank=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    class Meta:
        managed = False
        db_table = 'IUCN Data'

class IucnHabitat(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID') # Field name made lowercase. Field renamed to remove unsuitable characters.
    iucn_key = models.IntegerField(db_column='IUCN Key') # Field name made lowercase. Field renamed to remove unsuitable characters.
    habitat_number = models.CharField(db_column='Habitat Number', max_length=50) # Field name made lowercase. Field renamed to remove unsuitable characters.
    suitability = models.CharField(db_column='Suitability', max_length=50, blank=True) # Field name made lowercase.
    importance = models.CharField(db_column='Importance', max_length=50, blank=True) # Field name made lowercase.
    season = models.CharField(db_column='Season', max_length=50, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'IUCN Habitat'

class IucnThreat(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID') # Field name made lowercase. Field renamed to remove unsuitable characters.
    iucn_key = models.IntegerField(db_column='IUCN Key') # Field name made lowercase. Field renamed to remove unsuitable characters.
    threat_number = models.CharField(db_column='Threat Number', max_length=50) # Field name made lowercase. Field renamed to remove unsuitable characters.
    timing = models.CharField(db_column='Timing', max_length=255, blank=True) # Field name made lowercase.
    scope = models.CharField(db_column='Scope', max_length=255, blank=True) # Field name made lowercase.
    severity = models.CharField(db_column='Severity', max_length=255, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'IUCN Threat'

class ImagesManager(models.Manager):
    def getURL(self, id, resolution = None):


        import re

        images = self.model.objects.filter(species_id = id)


        thumbs = []
        for img in images:

            if 'wikipedia'in img.url:
                if not resolution:
                    thumbs.append(img.url)
                else:
                    match = re.search(r"[^a-zA-Z](commons)[^a-zA-Z]", img.url)
                    pos = match.end(1)
                    url = img.url[:pos] + "/thumb" + img.url[pos:]
                    file = url.split('/')[-1]
                    url = url + "/" + str(resolution) +"px-" +file
                    thumbs.append(url)
            else:
                thumbs.append(img.url)


        return thumbs



class Images(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID') # Field name made lowercase. Field renamed to remove unsuitable characters.
    url = models.CharField(db_column='URL', max_length=719) # Field name made lowercase.
    citation = models.CharField(db_column='Citation', max_length=255, blank=True) # Field name made lowercase.

    objects = ImagesManager()

    class Meta:
        managed = False
        db_table = 'Images'



class Names(models.Model):
    species_id = models.ForeignKey('Species', db_column='Species ID') # Field name made lowercase. Field renamed to remove unsuitable characters.
    accepted_name = models.CharField(db_column='Accepted Name', max_length=255, blank=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    accepted_authority = models.CharField(db_column='Accepted Authority', max_length=255, blank=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    synonym = models.CharField(db_column='Synonym', max_length=255) # Field name made lowercase.
    authority = models.CharField(db_column='Authority', max_length=511) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'Names'

class PaImagesManager(models.Manager):
    def getURL(self,id,resolution):
        import re
        images = self.model.objects.filter(pa_id = id)
        thumbs = []
        for img in images:
            if 'wikipedia'in img.url:
                match = re.search(r"[^a-zA-Z](commons)[^a-zA-Z]", img.url)
                pos = match.end(1)
                url = img.url[:pos] + "/thumb" + img.url[pos:]
                file = url.split('/')[-1]
                url = url + "/" + str(resolution) +"px-" +file
                thumbs.append(url)
            elif 'panoramio'in img.url:

                if resolution > 500:
                    size = "/large/"
                elif 500 >= resolution > 240:
                    size = "/medium/"
                else:
                    size = "/small/"
                url = re.sub(r"[^a-zA-Z](large)[^a-zA-Z]",size ,img.url)
                thumbs.append(url)
            else:
                thumbs.append(img.url)
        return thumbs



class PaImages(models.Model):
    pa_id = models.ForeignKey('ProtectedAreas', db_column='PA ID') # Field name made lowercase. Field renamed to remove unsuitable characters.
    url = models.CharField(db_column='URL', max_length=719) # Field name made lowercase.
    citation = models.CharField(db_column='Citation', max_length=511, blank=True) # Field name made lowercase.

    objects = PaImagesManager()
    class Meta:
        managed = False
        db_table = 'PA Images'



class SpeciesPa(models.Model):
    species_id = models.ForeignKey(Species, db_column='Species ID') # Field name made lowercase. Field renamed to remove unsuitable characters.
    pa_id = models.ForeignKey(ProtectedAreas, db_column='PA ID') # Field name made lowercase. Field renamed to remove unsuitable characters.
    class Meta:
        managed = False
        db_table = 'Species PA'

class Status(models.Model):
    species_id = models.ForeignKey(Species, db_column='Species ID', primary_key=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    protected = models.NullBooleanField(db_column='Protected') # Field name made lowercase.
    endemic = models.NullBooleanField(db_column='Endemic') # Field name made lowercase.
    cites = models.CharField(db_column='CITES', max_length=50, blank=True) # Field name made lowercase.
    nrdb = models.CharField(db_column='NRDB', max_length=50, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'Status'


