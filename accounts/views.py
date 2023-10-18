# DFB pg. 177
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from accounts.models import AuthorUser
from .forms import AuthorCreationForm
from accounts.forms import AuthorUpdateForm

class SignUpView(CreateView):
    form_class = AuthorCreationForm
    success_url = reverse_lazy('login')
    template_name = "registration/signup.html"

class AuthorUpdateView(UpdateView): # gpt
    model = AuthorUser
    form_class = AuthorUpdateForm
    template_name = 'editprofile.html'
    
    def get_success_url(self): # gpt
        return reverse_lazy('author_profile', kwargs={'pk': self.object.pk})