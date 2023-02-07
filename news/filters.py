from django_filters import FilterSet
from django import forms
from .models import Post

class NewsFilter(FilterSet):

  class Meta:
    model = Post
    fields = {
      'author__authorUser__username': ['exact'],
      'title': ['icontains'],
      'dateCreation': ['gt'],
    }