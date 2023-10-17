# DFB pg. 61
from django.urls import path
from .views import HomePageView, ListProfilesView, AuthorDetailView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"), # display HomePageView
    path("service/authors", ListProfilesView.as_view(), name="authors_list"), # display list of users on server; is this the exact url they want?
    path("service/authors/<int:pk>", AuthorDetailView.as_view(), name="author_profile"), # display author's profile
]