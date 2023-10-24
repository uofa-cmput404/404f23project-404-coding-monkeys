from django import forms
from .models import Posts

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ['title', 'description', 'content', 'visibility', 'categories']

    title = forms.CharField(required=True)

    description = forms.CharField(required=False, max_length=100)

    content = forms.Textarea()

    picture = forms.ImageField(label='Upload an image', required=False)

    visibility = forms.ChoiceField(choices=Posts.VISIBILITY_OPTIONS)

    # this will eventually become a popup where users can add categories
    categories = forms.CharField(required=True)

