from django.urls import path
from . import views

urlpatterns = [
    path('authors/<str:author_id>/posts/detail/', views.view_posts, name='detail'),
    path('authors/<str:author_id>/posts/<str:post_uuid>/edit', views.edit_post, name='edit_post'),
    path('authors/<str:author_id>/posts/<str:post_uuid>/delete', views.delete_post, name='delete_post'),
    path('new/', views.make_new_post, name='new_post'),
    path('delete_post/', views.edit_post, name='delete_post'),
    path('stream/', views.view_posts, name='stream'),
    path('like_post/', views.like_post_handler, name='like_post'),
    path('submit_comment/', views.submit_comment_handler, name='submit_comment'),
    path('open_comments/', views.open_comments_handler, name='open_comments'),
    path('test', views.test, name="test")
]