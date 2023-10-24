# DFB pg. 61
from django.urls import path
from .views import HomePageView, ListProfilesView, AuthorDetailView, FollowRequestsListView
from accounts.views import AuthorUpdateView
from . import views  # need this for follow to work 

urlpatterns = [
    path("", HomePageView.as_view(), name="home"), # display HomePageView
    path("service/authors/", ListProfilesView.as_view(), name="authors_list"), # display list of users on server; is this the exact url they want?
    path("service/authors/<int:pk>/", AuthorDetailView.as_view(), name="author_profile"), # display author's profile
    path("service/authors/<int:pk>/editprofile/", AuthorUpdateView.as_view(), name="author_edit"), # edit user's profile
    path("service/authors/<int:pk>/followed/", views.follow_author, name="author_followed"), 
    path("service/authors/<int:pk>/followrequests/", FollowRequestsListView.as_view(), name="author_requests"), 
    path("service/authors/<int:pk>/followrequests/accept/<int:fq_pk>", views.accept_fq, name="fq_accept"),
    path("service/authors/<int:pk>/followrequests/deny/<int:fq_pk>", views.deny_fq, name="fq_deny"),
]

#TODO are the urls supposed to have a terminating /? Because when I try service/authors/ it gives me a 404. Adding terminating / for now.