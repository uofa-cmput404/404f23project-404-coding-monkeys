# DFB pg. 166
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import AuthorCreationForm, AuthorChangeForm
from .models import AuthorUser
from posts.models import Posts

class CustomUserAdmin(UserAdmin): # give admin access to modifying and creating authors
    add_form = AuthorCreationForm
    form = AuthorChangeForm
    model = AuthorUser
    list_display = ["email", "username", "is_staff",] # display these fields in the user summary on the django admin page
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("github", "url", "profile_image",)}),) # allow these fields of an existing user to be edited in the django admin page
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("github", "url", "profile_image",)}),) # allow these fields to be set when creating a user in the django admin page

admin.site.register(AuthorUser, CustomUserAdmin) # register AuthorUser and Admin
admin.site.register(Posts)