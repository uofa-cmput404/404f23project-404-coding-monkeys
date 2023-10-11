# DFB pg. 167
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import AuthorUser

class AuthorCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = AuthorUser
        fields = UserCreationForm.Meta.fields + ("age",) # placeholder

class AuthorChangeForm(UserChangeForm):
    class Meta:
        model = AuthorUser
        fields = UserChangeForm.Meta.fields