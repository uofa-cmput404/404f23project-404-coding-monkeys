from django.urls import path
from . import views

urlpatterns = [
    path('authors/<str:author_id>/posts/', views.view_posts, name='detail'),
    path('new/', views.PostCreate.as_view(), name='new_post'),
    path('stream/', views.view_posts, name='stream'),
    path('update/', views.update_data, name='update_data'),
]
