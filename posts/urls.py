from django.urls import path
from . import views

urlpatterns = [
    path('authors/<str:author_id>/posts/', views.view_posts, name='detail'),
    path('new/', views.PostCreate.as_view(), name='new_post'),
    path('edit/', views.edit_post, name='edit_post'),
    path('stream/', views.view_posts, name='stream'),
    path('like_post/', views.like_post_handler, name='like_post'),
]
