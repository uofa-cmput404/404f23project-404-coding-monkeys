# DFB pg. 167
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import AuthorUser
from django.forms import ModelForm
from django import forms
import uuid


class AuthorCreationForm(UserCreationForm): # choose which fields should be displayed in sign-up form (password requested by default)
    class Meta(UserCreationForm):
        model = AuthorUser
        fields = ("username", "email", "github", "profile_image")

class AuthorChangeForm(UserChangeForm): # used to edit author profiles in django admin view; I don't think it can be accessed by the user
    class Meta:
        model = AuthorUser
        fields = UserChangeForm.Meta.fields

class AuthorUpdateForm(ModelForm): # used to allow authors to edit their own profile
    class Meta:
        model = AuthorUser
        fields = ["username", "email", "github", "profile_image"]