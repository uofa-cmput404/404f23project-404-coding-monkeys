# DFB pg. 177
from django.urls import path
from .views import SignUpView

urlpatterns = [
    path("/", SignUpView.as_view(), name="signup"), 
]

# note there is no login/ or logout/, because django handles their views automatically