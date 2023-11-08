# DFB pg. 177
from django.urls import path
from .views import SignUpView, AuthorUpdateView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"), 
    path('create_follow_request/', AuthorUpdateView.as_view(), name='create_follow_request'),
    path('author/update/<int:pk>/accept_friend_request/<int:friend_request_id>/', AuthorUpdateView.as_view(), name='accept_friend_request'),
    path('author/update/<int:pk>/deny_friend_request/<int:friend_request_id>/', AuthorUpdateView.as_view(), name='deny_friend_request'),
]

# note there is no login/ or logout/, because django handles their views automatically