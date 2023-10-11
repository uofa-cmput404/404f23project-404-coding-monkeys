# DFB pg. 166
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import AuthorCreationForm, AuthorChangeForm
from .models import AuthorUser

class CustomUserAdmin(UserAdmin):
    add_form = AuthorCreationForm
    form = AuthorChangeForm
    model = AuthorUser
    list_display = ["email", "username", "age", "is_staff",] # display these fields in the django admin page
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("age",)}),) # allow these fields to be edited for an admin(?)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("age",)}),) # allow these fields to be set when creating an admin(?)

admin.site.register(AuthorUser, CustomUserAdmin) # register AuthorUser and Admin