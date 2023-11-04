# DFB pg. 61
from django.urls import path
from .views import ListProfilesView, AuthorDetailView, FollowRequestsListView
from accounts.views import AuthorUpdateView
from . import views
from posts import views as post_views

urlpatterns = [
    path("", views.home_page_view, name="home"), # display homepage if you're not logged in/registered
    path("authors/list/", ListProfilesView.as_view(), name="authors_list"), # display list of users on server
    path("authors/<int:pk>/detail/", views.author_user_detail, name="author_profile"), # display given author's profile
    path("authors/<int:pk>/editprofile/", AuthorUpdateView.as_view(), name="author_edit"), # edit user's profile; sensitive
    path("authors/<int:pk>/followed/", views.follow_author, name="author_followed"), # dummy url for sending follow requests
    path("authors/<int:pk>/followrequests/", FollowRequestsListView.as_view(), name="author_requests"), # lists given user's friend requests; sensitive
    path("authors/<int:pk>/followrequests/accept/<int:fq_pk>/", views.accept_fq, name="fq_accept"), # dummy url for accepting a friend request
    path("authors/<int:pk>/followrequests/deny/<int:fq_pk>/", views.deny_fq, name="fq_deny"), # dummy url for denying a friend request

    # Author API Calls
    path("authors/<int:pk>/", views.api_single_author, name="api_single_author"),
    path("authors/", views.api_all_authors, name="api_all_authors"),

    # Follower API Calls
    path("authors/<int:pk>/followers/", views.api_follow_list, name="api_follow_list"),
    path("authors/<int:pk>/followers/<int:foreign_author_id>/", views.api_foreign_follower, name="api_foreign_follower"),

    # Post API Calls
    path("authors/<int:pk>/posts/<int:post_id>/", post_views.api_posts, name="api_posts"),
    path("authors/<int:pk>/posts/", post_views.api_post_creation, name="api_post_creation")
]