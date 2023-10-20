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

    def form_valid(self, form): # CHATGPT - 2023-10-13 Prompt #1
        if not form.cleaned_data.get('profile_image'): # check if user provided value for profile_image field
            form.instance.profile_image = 'https://t3.ftcdn.net/jpg/05/71/08/24/360_F_571082432_Qq45LQGlZsuby0ZGbrd79aUTSQikgcgc.jpg' # if they didn't set to default avatar; CHATGPT - 2023-10-13 Prompt #2

        return super().form_valid(form) # save the user or perform any other necessary actions

class AuthorUpdateView(UpdateView): 
    model = AuthorUser
    form_class = AuthorUpdateForm
    template_name = 'editprofile.html'
    
    def get_success_url(self): # gpt
        return reverse_lazy('author_profile', kwargs={'pk': self.object.pk})