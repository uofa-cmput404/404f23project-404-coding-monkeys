# DFB pg. 61
from django.urls import path
from .views import ListProfilesView, AuthorDetailView, FollowRequestsListView
from accounts.views import AuthorUpdateView
from . import views

urlpatterns = [
    path("", views.home_page_view, name="home"), # display homepage if you're not logged in/registered
    path("authors/", ListProfilesView.as_view(), name="authors_list"), # display list of users on server
    path("authors/<int:pk>/", views.author_user_detail, name="author_profile"), # display given author's profile
    path("authors/<int:pk>/editprofile/", AuthorUpdateView.as_view(), name="author_edit"), # edit user's profile; sensitive
    path("authors/<int:pk>/followed/", views.follow_author, name="author_followed"), # dummy url for sending follow requests
    path("authors/<int:pk>/followrequests/", FollowRequestsListView.as_view(), name="author_requests"), # lists given user's friend requests; sensitive
    path("authors/<int:pk>/followrequests/accept/<int:fq_pk>/", views.accept_fq, name="fq_accept"), # dummy url for accepting a friend request
    path("authors/<int:pk>/followrequests/deny/<int:fq_pk>/", views.deny_fq, name="fq_deny"), # dummy url for denying a friend request

    path("api/authors/<int:pk>/", views.get_author, name="get_author"), # get author by id
    path("api/authors/", views.get_authors, name="get_authors"), # get all authors
]