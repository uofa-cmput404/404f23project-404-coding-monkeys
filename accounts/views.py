# DFB pg. 177
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from accounts.models import AuthorUser
from .forms import AuthorCreationForm
from accounts.forms import AuthorUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from .models import FollowRequests
from django.http import JsonResponse

class SignUpView(CreateView):
    form_class = AuthorCreationForm
    success_url = reverse_lazy('login')
    template_name = "registration/signup.html"

    def form_valid(self, form): # CHATGPT - 2023-10-13 Prompt #1
        if not form.cleaned_data.get('profile_image'): # check if user provided value for profile_image field
            form.instance.profile_image = 'https://t3.ftcdn.net/jpg/05/71/08/24/360_F_571082432_Qq45LQGlZsuby0ZGbrd79aUTSQikgcgc.jpg' # if they didn't set to default avatar; CHATGPT - 2023-10-13 Prompt #2

        return super().form_valid(form) # save the user or perform any other necessary actions

class AuthorUpdateView(LoginRequiredMixin, UserPassesTestMixin,UpdateView): 
    model = AuthorUser
    form_class = AuthorUpdateForm
    template_name = 'editprofile.html'

    def test_func(self): # CHATGPT - 2023-10-30 Prompt #1
        user_id = self.kwargs.get('pk')  # Assuming 'pk' is the user ID in the URL.
        return self.request.user.id == user_id

    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    def get_success_url(self): # gpt
        return reverse_lazy('author_profile', kwargs={'pk': self.object.pk})
    
    def create_follow_request(self, request):
        if request.method=='POST':
            data=request.POST
            follow_request = FollowRequests.objects.create(
                summary=data.get('summary'),
                requester=data.get('actor'),
                recipient=data.get('object'),
                status='pending' 
            )
            follow_request.save()
            return JsonResponse({'message': 'Friend/Follow request created successfully.'})
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=400)
    def accept_friend_request(self, request, friend_request_id):
        if request.method == 'POST':
            try:
                friend_request = FollowRequests.objects.get(id=friend_request_id)
            except FollowRequests.DoesNotExist:
                return JsonResponse({'error': 'Friend request not found'}, status=404)

            if friend_request.status == 'pending':
                friend_request.status = 'accepted'
                friend_request.save()
                #send status update to inbox
                return JsonResponse({'message': 'Friend request accepted successfully.'})
            else:
                return JsonResponse({'error': 'Friend request has already been accepted.'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=400)
    def deny_friend_request(self, request, friend_request_id):
        if request.method == 'POST':
            try:
                friend_request = FollowRequests.objects.get(id=friend_request_id)
            except FollowRequests.DoesNotExist:
                return JsonResponse({'error': 'Friend request not found'}, status=404)

            if friend_request.status == 'pending':
                friend_request.status = 'rejected'
                friend_request.save()
                #send status update to inbox

                return JsonResponse({'message': 'Friend request denied successfully.'})
            else:
                return JsonResponse({'error': 'Friend request has already been accepted or rejected.'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=400)