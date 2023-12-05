from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_all_connections, name="connections_page"), # display homepage if you're not logged in/registered
    path("refresh-cache/", views.refreshCache, name="refresh-cache"), # display homepage if you're not logged in/registered
]