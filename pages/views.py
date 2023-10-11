from django.views.generic import TemplateView

# DFB pg. 60
class HomePageView(TemplateView): # basic generic view that just displays template
    template_name = "home.html" 
