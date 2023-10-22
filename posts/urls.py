from django.urls import path
from . import views

urlpatterns = [
    path('authors/<str:author_id>/posts/<str:post_id>', views.DetailView.as_view(), name='detail'),
    path('authors/<str:author_id>/posts/new', views.upload, name='new'),
    path('authors/<str:author_id>/posts/', views.upload, name='creation'),
]
