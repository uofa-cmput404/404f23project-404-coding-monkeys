import json
from django.http import HttpResponse

from django.forms.models import model_to_dict
from django.views.generic import TemplateView, ListView, DetailView
from accounts.models import AuthorUser, FollowRequests

# wip
from django.core import serializers
from django.shortcuts import get_object_or_404, redirect 

# DFB pg. 60
class HomePageView(TemplateView): # basic generic view that just displays template
    template_name = "home.html" 

class ListProfilesView(ListView): # basic generic view that just displays template
    model = AuthorUser
    template_name = "listprofiles.html" 
    context_object_name = 'authors_list'

class AuthorDetailView(DetailView): # basic generic view that just displays template
    model = AuthorUser
    template_name = "authorprofile.html" 
    context_object_name = 'author'

def follow_author(request, pk): # CHATGPT - 2023-10-20 Prompt #1
    # https://stackoverflow.com/questions/74199737/how-to-create-django-model-by-pressing-button - general structure followed for how to create a model instance in db via button press
    # https://stackoverflow.com/questions/28071750/redirecting-a-view-to-another-view-in-django-python - how to redirect in django via url pattern
    user = request.user # get db information of current user
    author = get_object_or_404(AuthorUser, pk=pk) # get db information of author to follow

    user_data = { # user fields to be added to json
        'type': user.type,
        'username': user.username,
        'host': user.host,
        'url': user.url,
        'github': user.github,
        'profile_image': user.profile_image
    }

    author_data = {# author to follow fields to be added to json
        'type': author.type,
        'username': author.username,
        'host': author.host,
        'url': author.url,
        'github': author.github,
        'profile_image': author.profile_image,
    }

    # create FollowRequest instance in db
    FollowRequests.objects.get_or_create(
        summary="{} wants to follow {}".format(user.username, author.username),
        requester=user_data,
        recipient=author_data
    )

    return redirect('author_profile', pk=pk)


    """ 
    # proper way of serializing; doesn't seem to be an option to only choose just some of the fields
    #https://stackoverflow.com/questions/757022/how-do-you-serialize-a-model-instance-in-django - how to serialize stuff
    #https://stackoverflow.com/questions/60376352/why-there-is-like-bunch-of-backslash-in-my-json-output - how to fix the backslashes everywhere
    author_json = serializers.serialize("json", [AuthorUser.objects.get(id=pk)])
    author_json = json.loads(author_json)
    """

def view_my_profile(request):
    user = request.user # get db information of current user
    author_obj = get_object_or_404(AuthorUser, username=user) # get db information of author to follow
    author_dict = model_to_dict(author_obj)
    return redirect('author_profile', pk=author_dict.get("id"))