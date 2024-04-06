from django import forms
from .models import Video


# Form for adding and editing video entries
class VideoForm(forms.ModelForm):
    class Meta:
        model = Video  # Specify the model for the form
        fields = ['name', 'url', 'notes']  # Specify the fields to include in the form


# Form for searching videos
class SearchForm(forms.Form):
    # Field for entering the search term
    search_term = forms.CharField()