# DFB pg. 167
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import AuthorUser

class AuthorCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = AuthorUser
        fields = ("username", "email", "age",) # choose which fields should be displayed in sign-up form (password requested by default)

class AuthorChangeForm(UserChangeForm):
    class Meta:
        model = AuthorUser
        fields = UserChangeForm.Meta.fields