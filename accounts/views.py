# DFB pg. 177
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
import jwt
from accounts.models import AuthorUser
from accounts.serializers import TokenSerializer
from connections.caches import AuthorCache
from django_project import settings
from .forms import AuthorCreationForm
from accounts.forms import AuthorUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from util import get_id_from_url, get_part_from_url
import uuid
from django.shortcuts import render#for Error_Return and errorPage.html

def Error_Return(request):

    my_error="Error 404 - Page Not Found"
    return render(request, 'errorPage.html', {'errorCode':my_error})
                  



class SignUpView(CreateView):
    form_class = AuthorCreationForm
    success_url = reverse_lazy('login')
    template_name = "registration/signup.html"

    def form_valid(self, form): # CHATGPT - 2023-10-13 Prompt #1
        form.instance.uuid = str(uuid.uuid4()) # generate uuid for user
        if not form.cleaned_data.get('profile_image'): # check if user provided value for profile_image field
            form.instance.profile_image = 'https://t3.ftcdn.net/jpg/05/71/08/24/360_F_571082432_Qq45LQGlZsuby0ZGbrd79aUTSQikgcgc.jpg' # if they didn't set to default avatar; CHATGPT - 2023-10-13 Prompt #2
        return super().form_valid(form) # save the user or perform any other necessary actions

class AuthorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView): 
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
        return reverse_lazy('author_detail', kwargs={'host_id': 0, 'uuid': self.object.uuid})


# Create your views here.
@swagger_auto_schema(
    methods=['POST'], 
    tags=['remote','token'],
    operation_description="Refer to the following: <a href='https://chimp-chat-1e0cca1cc8ce.herokuapp.com/extra/docs#AuthCookie'>Section</a>",
    request_body=TokenSerializer,
    responses={
        200: openapi.Response("Success."),
        400: openapi.Response("Bad Request."),
    }
)
@api_view(["POST"])
def generate_jwt_token(request):
    if request.method == 'POST':
        serializer = TokenSerializer(data=dict(request.data))
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        jwt_token = jwt.encode(serializer.validated_data, settings.SECRET_KEY, algorithm='HS256')
    
        response = JsonResponse({'message': 'Succesfully set cookie.'})
        response.set_cookie('ChimpChatToken', jwt_token, httponly=True, secure=True)  # Make sure to set 'secure' to True in a production environment

        return response

def decode_cookie(jwt_token):
    if jwt_token:
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])

            return payload
        except:
            return None
    
    return None