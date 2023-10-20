from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, DetailView
from accounts.models import AuthorUser

from posts.models import Posts # debug

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

def follow_author(request, pk):
    print("TRIGGERED")
    Posts.objects.get_or_create(title="your shitty follow button is working!")
    return HttpResponse(None)