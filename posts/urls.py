from django.urls import path
from . import views

urlpatterns = [
    path('authors/<str:author_id>/posts/<str:post_id>', views.view_posts, name='detail'),
    path('authors/<str:author_id>/posts/', views.PostCreate.as_view(), name='creation'),
    path('redir/', views.redir_create, name='redir_create'),
    path('new/', views.PostCreate.as_view(), name='new'),
    path('all/', views.view_posts, name='all'),
]
