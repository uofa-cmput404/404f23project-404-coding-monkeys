from django.urls import path
from . import views

urlpatterns = [
    path('<str:uuid>/', views.view_user_posts, name='view_author_posts'),
    path('authors/<str:author_id>/posts/detail/', views.view_posts, name='detail'),
    path('authors/<str:author_id>/posts/<str:post_uuid>/edit', views.edit_post, name='edit_post'),
    path('<str:post_uuid>/delete', views.delete_post, name='delete_post'),
    path('public/', views.public_posts, name='public'),
    path('test/', views.test, name='test'),
    path('new/', views.make_new_post, name='new_post'),
    path('delete_post/', views.edit_post, name='delete_post_the_sequel'),
    path('stream/', views.post_stream, name='stream'),
    path('my-stream/', views.personal_stream, name='personal_stream'),
    path('like_post/', views.like_post_handler, name='like_post'),
    path('submit_comment/', views.submit_comment_handler, name='submit_comment'),
    path('open_comments/', views.open_comments_handler, name='open_comments'),
    path('like_comment/', views.like_comment_handler, name='like_comment'),
    path('share_post/', views.share_post_handler, name='share_post'),
]