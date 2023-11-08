# DFB pg. 177
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from accounts.models import AuthorUser
from .forms import AuthorCreationForm
from accounts.forms import AuthorUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
import uuid

class SignUpView(CreateView):
    form_class = AuthorCreationForm
    success_url = reverse_lazy('login')
    template_name = "registration/signup.html"

    def form_valid(self, form): # CHATGPT - 2023-10-13 Prompt #1
        form.instance.uuid = str(uuid.uuid4()) # generate uuid for user
        if not form.cleaned_data.get('profile_image'): # check if user provided value for profile_image field
            form.instance.profile_image = 'https://t3.ftcdn.net/jpg/05/71/08/24/360_F_571082432_Qq45LQGlZsuby0ZGbrd79aUTSQikgcgc.jpg' # if they didn't set to default avatar; CHATGPT - 2023-10-13 Prompt #2
        return super().form_valid(form) # save the user or perform any other necessary actions

class AuthorUpdateView(LoginRequiredMixin, UserPassesTestMixin,UpdateView): 
    model = AuthorUser
    form_class = AuthorUpdateForm
    template_name = 'editprofile.html'
    slug_url_kwarg = "uuid"

    def test_func(self): # CHATGPT - 2023-10-30 Prompt #1
        user_id = self.kwargs.get('uuid')  # Assuming 'uuid' is the user ID in the URL.
        return self.request.user.uuid == user_id

    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    def get_success_url(self): # gpt
        return reverse_lazy('author_profile', kwargs={'uuid': self.object.uuid})