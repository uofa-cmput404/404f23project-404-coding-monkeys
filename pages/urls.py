# DFB pg. 61
from django.urls import path
from .views import ListProfilesView, AuthorDetailView, FollowRequestsListView
from accounts.views import AuthorUpdateView
from . import views
from posts import views as post_views
from inbox import views as inbox_views

urlpatterns = [
    path("", views.home_page_view, name="home"), # display homepage if you're not logged in/registered

    # Need to put API calls first so that they don't get caught by the LOCAL paths
    # ======================================================================================================================================

    # Author API Calls
    path("authors/<str:uuid>/", views.api_single_author, name="api_single_author"),
    path("authors/", views.api_all_authors, name="api_all_authors"),

    # Follower API Calls
    path("authors/<str:uuid>/followers/", views.api_follow_list, name="api_follow_list"),
    path("authors/<str:uuid>/followers/<str:foreign_author_id>/", views.api_foreign_follower, name="api_foreign_follower"),

    # Post API Calls
    path("authors/<str:uuid>/posts/<str:post_id>/", post_views.api_posts, name="api_posts"),
    path("authors/<str:uuid>/posts/", post_views.api_post_creation, name="api_post_creation"),

    # Inbox API Calls
    path("authors/<str:uuid>/inbox/", inbox_views.api_inbox, name="api_inbox"),

    #Post Image API calls
    path('authors/<str:uuid>/posts/<str:post_id>/image/', post_views.serve_image, name='get_image_post'),

    # Comment API Calls
    path('authors/<str:uuid>/posts/<str:post_id>/comments/', post_views.api_comments, name='api_comments'),

    # Likes API Calls
    path('authors/<str:uuid>/posts/<str:post_id>/likes/', post_views.api_post_likes, name='api_post_likes'),
    path('authors/<str:uuid>/posts/<str:post_id>/comments/<str:comment_id>/likes/', post_views.api_comment_likes, name='api_comment_likes'),

    # Public Liked API Calls
    path('authors/<str:uuid>/liked/', post_views.api_author_liked, name='api_author_liked'),

    # Local paths
    # ======================================================================================================================================

    # restful and connection-cognizant author profile
    path("authors/<int:host_id>/<str:uuid>/", views.render_author_detail, name="author_detail"), # display given author's profile
    path("authors/profile/determine-args/", views.get_author_detail, name="determine_author_detail"), # edit user's profile; sensitive

    # path("authors/<str:uuid>/posts/<str:post_id>/post-image", post_views.serve_image, name="serve_image"),

    path("authors/profiles/listall", views.list_profiles, name="authors_list"), # display list of users on server
    
    path("authors/<slug:uuid>/editprofile/", AuthorUpdateView.as_view(), name="author_edit"), # edit user's profile; sensitive

    path("follow_requests/", views.follow_requests, name="follow_requests"), # display list of follow requests
    path("accept_fq", views.accept_fq, name="accept_fq"), # dummy url for accepting a friend request
    path("deny_fq", views.deny_fq, name="deny_fq"), # dummy url for denying a friend request
    path("authors/<str:uuid>/unfollowed/<str:rq_uuid>/", views.unfollow_author, name="author_unfollow"), # dummy url for unfollowing an author

    path('authors/<str:author_uuid>/posts/<str:post_uuid>/unlisted', post_views.unlisted_post, name='single_post_view'),
]