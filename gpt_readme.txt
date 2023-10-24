This file contains all major usages of AI. The lines in the code where the prompt was used or applied 
in some way are noted with the corresponding date and prompt #.

EXAMPLE FORMAT:
AI name - date - prompt #
Code Input + Prompt
Output
Any notes
-----

CHATGPT - 2023-10-13 Prompt #1

"im using a generic CreateView and form for my django registration page. 
I have a certain url field that the user may enter, but if they choose not to, will default to a link I've already set. 
The problem is the form starts with the default field already  filled in, which is a bit ugly. 
Is there any way to set this field to the default link ONLY if the user doesn't enter anything for that field, 
and only after they've submitted the sign up form?"

class RegistrationView(CreateView):
    model = YourUserModel  # Replace with your actual user model
    form_class = YourRegistrationForm
    template_name = 'registration.html'  # Replace with your template

    def form_valid(self, form):
        # Check if the user provided a value for the URL field
        if not form.cleaned_data.get('url_field'):
            # If the field is empty, set it to the default value
            form.cleaned_data['url_field'] = 'https://example.com'

        # Save the user or perform any other necessary actions
        return super().form_valid(form)

Notes: adapted to work with profile_image
-----

CHATGPT - 2023-10-13 Prompt #2

my form_valid() function isn't working; when I look at a user's profile in django admin, the profile_image field is empty, 
even if they didn't enter one (if they don't enter one, it's supposed to set it as that link I'm setting there)

class SignUpView(CreateView):
    form_class = AuthorCreationForm
    success_url = reverse_lazy('login')
    template_name = "registration/signup.html"

    def form_valid(self, form):
        if not form.cleaned_data.get('profile_image'):
            form.instance.profile_image = 'https://t3.ftcdn.net/jpg/05/71/08/24/360_F_571082432_Qq45LQGlZsuby0ZGbrd79aUTSQikgcgc.jpg'

        return super().form_valid(form)

Notes: used form.instance.profile_image line to get the previous prompt working properly.

-----

CHATGPT - 2023-10-20 Prompt #1

INPUT:
def follow_author(request, pk):
    """ user_id = request.user.get_username() # https://stackoverflow.com/questions/16906515/how-to-get-the-username-of-the-logged-in-user-in-django
    author_id = pk

    # https://www.tutorialspoint.com/how-to-convert-models-data-into-json-in-django
    # https://stackoverflow.com/questions/4300365/django-database-query-how-to-get-object-by-id
    user_data = serializers.serialize('json', AuthorUser.objects.get(user_id)) # user requesting follow
    author_data = serializers.serialize('json', AuthorUser.objects.get(author_id)) # author to follow

    FollowRequests.objects.get_or_create(summary="add proper summary here", requester=user_data, recipient=author_data)
    
    return HttpResponse(None) """
    user = request.user  # Get the current user
    #author = get_object_or_404(AuthorUser, pk=pk)  # Get the AuthorUser instance with the specified primary key

    # Define a list of fields you want to include in the serialized output
    wanted_fields = ['type', 'username', 'host', 'url', 'github', 'profile_image']  # Replace with the fields you want

    # https://stackoverflow.com/questions/757022/how-do-you-serialize-a-model-instance-in-django - how to serialize stuff
    # https://stackoverflow.com/questions/60376352/why-there-is-like-bunch-of-backslash-in-my-json-output - how to fix the backslashes everywhere

    
    author_json = serializers.serialize("json", [AuthorUser.objects.get(id=pk)])
    author_json = json.loads(author_json)

    FollowRequests.objects.get_or_create(
        summary="add proper summary here",
        #requester=user_data,
        recipient=author_json
    )

    return HttpResponse(200)

how do I change this code so I only serialize some, not all, of the AuthorUser fields

OUTPUT:
def follow_author(request, pk):
    user = request.user

    # Define a list of fields you want to include in the serialized output
    wanted_fields = ['type', 'username', 'host', 'url', 'github', 'profile_image']

    # Get the AuthorUser instance with the specified primary key
    author = get_object_or_404(AuthorUser, pk=pk)

    # Create a dictionary with the selected fields
    author_data = {
        'type': author.type,
        'username': author.username,
        'host': author.host,
        'url': author.url,
        'github': author.github,
        'profile_image': author.profile_image,
    }

    # Serialize the custom data dictionary
    author_json = json.dumps([author_data])

    # Create the FollowRequests object
    FollowRequests.objects.get_or_create(
        summary="add proper summary here",
        requester=user,
        recipient=author_json
    )

    return HttpResponse(200)

Notes: used GPT suggestion modification of original code, and took of the approach of using a dictionary to manually select which fields
to select for JSON (don't need all of them).
                    
-----

CHATAGPT - 2023-10-22 - Prompt #1

INPUT:
# DFB pg. 61
from django.urls import path
from .views import HomePageView, ListProfilesView, AuthorDetailView, FollowRequestsListView
from accounts.views import AuthorUpdateView
from . import views  # need this for follow to work 

urlpatterns = [
    path("", HomePageView.as_view(), name="home"), # display HomePageView
    path("service/authors/", ListProfilesView.as_view(), name="authors_list"), # display list of users on server; is this the exact url they want?
    path("service/authors/<int:pk>/", AuthorDetailView.as_view(), name="author_profile"), # display author's profile
    path("service/authors/<int:pk>/editprofile/", AuthorUpdateView.as_view(), name="author_edit"), # edit user's profile
    path("service/authors/<int:pk>/followed/", views.follow_author, name="author_followed"), 
    path("service/authors/<int:pk>/followrequests/", FollowRequestsListView.as_view(), name="author_requests"), 
    path("service/authors/<int:pk>/followrequests/accept/", views.accept_fq, name="fq_accept"), # 
    path("service/authors/<int:pk>/followrequests/deny/", views.deny_fq, name="fq_deny"),
]

#TODO are the urls supposed to have a terminating /? Because when I try service/authors/ it gives me a 404. Adding terminating / for now.

User
I have a problem, for my fq_accept and fq_deny urls, I want to pass a second  int value that contains the pk of the followrequest object I want to send to the view. the problem is it's already expecting the authoruser pk, but I can't seem to return more than one value from inside my accept_fq and deny_fq views; what should I do?

OUTPUT:
{% for follow_request in follow_requests %}
    <p>Follow Request from {{ follow_request.sender.username }}</p>
    <a href="{% url 'fq_accept' author_pk=authoruser.pk fq_pk=follow_request.pk %}">Accept</a>
    <a href="{% url 'fq_deny' author_pk=authoruser.pk fq_pk=follow_request.pk %}">Deny</a>
{% endfor %}

Note: used for guidance on how to return multiple values from template, and setup the placeholders in the url properly.
