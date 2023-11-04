from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_all_connections, name="connections_page"), # display homepage if you're not logged in/registered
]