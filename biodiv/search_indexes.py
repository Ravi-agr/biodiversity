import datetime
from haystack import indexes
from biodiv.models import Species, CommonNames, Names


class SpeciesIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
	def get_model(self):
		return Species

	def index_queryset(self, using=None):
		"""Used when the entire index for model is updated."""
		return self.get_model().objects
		
class CommonNamesIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
	def get_model(self):
		return CommonNames

	def index_queryset(self, using=None):
		"""Used when the entire index for model is updated."""
		return self.get_model().objects

class NamesIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    def get_model(self):
        return Names

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects