from django import forms
from .models import Posts
import uuid

class PostForm(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ['title', 'description', 'content', 'visibility', 'categories']

    uuid = forms.CharField(required=False)

    title = forms.CharField(required=True)

    description = forms.CharField(required=False, max_length=100)

    content = forms.Textarea()

    picture = forms.ImageField(label='Upload an image', required=False)

    visibility = forms.ChoiceField(choices=Posts.VISIBILITY_OPTIONS)

    sharedWith = forms.CharField(required=False)

    # this will eventually become a popup where users can add categories
    categories = forms.CharField(required=True)

