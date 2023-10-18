# DFB pg. 61
from django.urls import path
from .views import HomePageView, ListProfilesView, AuthorDetailView
from accounts.views import AuthorUpdateView # bit of a mess having the view in the accounts app, but we can tidy up and refactor later

urlpatterns = [
    path("", HomePageView.as_view(), name="home"), # display HomePageView
    path("service/authors/", ListProfilesView.as_view(), name="authors_list"), # display list of users on server; is this the exact url they want?
    path("service/authors/<int:pk>/", AuthorDetailView.as_view(), name="author_profile"), # display author's profile
    path("service/authors/<int:pk>/editprofile/", AuthorUpdateView.as_view(), name="author_edit"), # edit user's profile
]

#TODO are the urls supposed to have a terminating /? Because when I try service/authors/ it gives me a 404. Adding terminating / for now.