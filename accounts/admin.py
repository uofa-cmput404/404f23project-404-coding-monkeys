# DFB pg. 166
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import AuthorCreationForm, AuthorChangeForm
from .models import AuthorUser, Followers, WhitelistController
from posts.models import Posts
from accounts.models import FollowRequests
from django.http import HttpResponseRedirect

class CustomUserAdmin(UserAdmin): # give admin access to modifying and creating authors
    add_form = AuthorCreationForm
    form = AuthorChangeForm
    model = AuthorUser
    list_display = ["email", "username", "is_staff",] # display these fields in the user summary on the django admin page
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("github", "url", "profile_image",)}),) # allow these fields of an existing user to be edited in the django admin page
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("github", "url", "profile_image",)}),) # allow these fields to be set when creating a user in the django admin page

class WhitelistControllerAdmin(admin.ModelAdmin): # https://stackoverflow.com/a/1505259 - spookylukey - function adapted to limit number of WhiteListController objects to 1
    def has_add_permission(self, request, obj=None):
        return False

# https://stackoverflow.com/questions/40833324/django-attributeerror-alias-object-has-no-attribute-urls
# WARNING: every model (except user ones I guess) must be registered on its own line
admin.site.register(AuthorUser, CustomUserAdmin) # register AuthorUser and Admin
admin.site.register(WhitelistController, WhitelistControllerAdmin)
admin.site.register(Posts)
admin.site.register(FollowRequests)
admin.site.register(Followers)