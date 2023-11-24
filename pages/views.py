import json
import enum
from turtle import pen
from venv import create
from django.http import HttpResponse

from django.middleware.csrf import get_token
from django.forms.models import model_to_dict
from django.views.generic import TemplateView, ListView, DetailView
from accounts.models import AuthorUser, FollowRequests, Followers

# wip
from django.core import serializers
from django.shortcuts import get_object_or_404, redirect, render 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from connections.views import get_auth_for_host

from .util import AuthorDetail
from .seralizers import AuthorDetailSerializer, AuthorUserSerializer, FollowRequestsSerializer, FollowerListSerializer, AuthorUserReferenceSerializer, ResponseAuthorsSerializer, ResponseFollowersSerializer
from static.vars import ENDPOINT, HOSTS
import requests
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from requests.auth import HTTPBasicAuth

# DFB pg. 60
def home_page_view(request): # basic generic view that just displays template
    if (request.user.is_authenticated): # if user is logged in, immediately redirect to posts stream
        return redirect('stream')
    
    return render(request, 'home.html') # otherwise they're not logged in, and should be prompted with the homepage to login or signup

@DeprecationWarning
class ListProfilesView(ListView): # basic generic view that just displays template
    model = AuthorUser
    template_name = "listprofiles.html" 
    context_object_name = 'authors_list'


# RESTful List of profiles
# ================================================================================================================================
# new implementation, acquiring profiles from all connected hosts including local
def list_profiles(request):
    # the api url to get list of profiles
    url = "/authors/"
    all_authors = []

    # for all connected hosts
    for host in HOSTS:
        full_url = host + url
        headers = {"Accept": "application/json"}

        auth = get_auth_for_host(host)
        # send request to get list of profiles
        response = requests.get(full_url, headers=headers, auth=HTTPBasicAuth(auth[0], auth[1]))

        # if 2XX response code
        if response.ok:
            authors = response.json().get("items")
            # iterate through authors and check that they are valid using serializer, exclude authors that are deemed invalid (missing or misformed data)
            for author in authors:
                serializer = AuthorUserReferenceSerializer(data=author)
                if not serializer.is_valid():
                    continue
                valid_author = serializer.validated_data
                valid_author["uuid"] = get_id_from_url(valid_author["url"])
                all_authors.append(valid_author)

    return render(request, 'listprofiles.html', {'authors_list': all_authors})

@DeprecationWarning
class AuthorDetailView(DetailView): # basic generic view that just displays template
    model = AuthorUser
    template_name = "authorprofile.html" 
    context_object_name = 'author'

def author_user_detail(request, uuid):
    author_user = AuthorUser.objects.get(uuid=uuid)
    try: # author to be viewed has at least one follower
        followers = Followers.objects.get(author=author_user)
        num_followers = len(followers.followers)
        viewing_user = request.user.username
        already_following = False
        follower_avatars = {}

        for i in range(0, num_followers):
            #print(followers.followers[i]['username']) # debug
            if (followers.followers[i]['username'] == viewing_user): # if the the viewing/logged in user is in the viewed author's followers list, hide follow button
                already_following = True

            # handle showing follower profile images
            follower_username = followers.followers[i]['username'] #TODO replace above? don't want to break anything
            follower_info = AuthorUser.objects.get(username=follower_username)
            follower_avatars[follower_username] = follower_info.profile_image # add follower's profile image url to dictionary, with their username as key

    except: # author to be viewed has no followers (no instance in db yet)
        already_following = False
        followers = None # safe?
        follower_avatars = {}

    # handle pending friend requests (hide follow button, show "requested")
    pending_request = False # does author have a pending fq from user?
    try:
        FollowRequests.objects.get(summary='{} wants to follow {}'.format(request.user.username, author_user.username)) # a bit jank to search by summary; could add author and user as foreign keys to FollowRequest?
        pending_request = True # a pending request exists
    except:
        pending_request = False # a pending request does not exist

    return render(request, 'authorprofile.html', {'author': author_user, 'followers': followers, 'already_following': already_following, 'follower_avatars': follower_avatars, 'pending_request': pending_request})



# RESTful Author Profile
# ================================================================================================================================

def get_id_from_url(url):
    if url:
        url = url[:-1] if url[-1] == "/" else url
        url = url.split("/")
        return url[-1]
    return ""

def get_part_from_url(url, part):
    # part is one of authors, posts, or comments and will return the id for that part
    if url:
        url = url[:-1] if url[-1] == "/" else url
        url = url.split("/")

        index = 0
        while index < len(url) and url[index] != part:
            index += 1
        
        # return id right after we find the part
        return url[index+1] if index < len(url) - 1 else ""
    return ""

def get_author_detail(request):

    author_detail_url = request.POST.get("get_url")
    plain_id = get_id_from_url(author_detail_url)

    host = request.POST.get("host")
    host = host[:-1] if host[-1] == "/" else host
    index = HOSTS.index(host)

    return HttpResponse(content=json.dumps({"host_index":index, "uuid": plain_id}))

def render_author_detail(request, host_id, uuid):
    global HOSTS
    # grab the author information
    path = HOSTS[host_id] + "/authors/" + uuid + "/"
    auth = get_auth_for_host(HOSTS[host_id])
    print("auth object", auth)
    response = requests.get(path, auth=HTTPBasicAuth(auth[0], auth[1]))

    if response.ok:
        author = response.json()
        # already validated from the originating view, so do not have to check for serialization
        author["uuid"] = get_id_from_url(author["url"])
    else:
        # TODO render and error page
        return HttpResponse(content="Author not found", status=response.status_code)

    # grab the followers information
    all_followers = []

    path = HOSTS[host_id] + "/authors/" + uuid + "/followers/"
    response = requests.get(path, auth=HTTPBasicAuth(auth[0], auth[1]))
    if response.ok:
        followers = response.json()
        for follower in followers["items"]:
            # serialize to check if everything is in expected format
            serializer = AuthorUserReferenceSerializer(data=follower)
            # exclude if invalid
            if not serializer.is_valid():
                continue
            # assign uuid from full url
            valid_follower = serializer.validated_data
            valid_follower["uuid"] = get_id_from_url(valid_follower["url"])
            # append valid follower to list to pass into view

            # grab the latest profile image
            path = HOSTS[host_id] + "/authors/" + valid_follower["uuid"] + "/"
            response = requests.get(path, auth=HTTPBasicAuth(auth[0], auth[1]))
            # if response was good, get pfp from response data
            if response.ok:
                data = response.json()
                valid_follower["profileImage"] = data.get("profileImage")

            all_followers.append(valid_follower)

    # check if we are following the user in view
    following = False
    path = HOSTS[host_id] + "/authors/" + uuid + "/followers/" + request.user.uuid + "/"
    response = requests.get(path, auth=HTTPBasicAuth(auth[0], auth[1]))
    if response.ok:
        following = True                            

    # check if we have a request for the user in view
    follow_rq = FollowRequests.objects.filter(requester_uuid=request.user.uuid , recipient_uuid=uuid)
    requested = len(follow_rq) > 0

    return render(request, 'authorprofile.html', {'author': author, 'followers': all_followers, 'already_following': following, 'pending_request': requested})


class FollowRequestsListView(LoginRequiredMixin, UserPassesTestMixin, ListView): # basic generic view that just displays template
    model = FollowRequests
    template_name = "followrequests.html" 
    context_object_name = 'requests_list'

    def test_func(self): # CHATGPT - 2023-10-30 Prompt #1
        user_id = self.kwargs.get('uuid')  # Assuming 'uuid' is the user ID in the URL.
        return self.request.user.uuid == user_id

    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    def get_follower_info(request_data):
        return {
        "type": "author",
        "id": request_data.get("uuid"),
        "host": request_data.get("host"),
        "username": request_data.get("displayName"),
        "url": request_data.get("url"),
        "github": request_data.get("github"),
        "profile_image": request_data.get("profileImage")
        }

    

def follow_author(request, uuid): # CHATGPT - 2023-10-20 Prompt #1
    # https://stackoverflow.com/questions/74199737/how-to-create-django-model-by-pressing-button - general structure followed for how to create a model instance in db via button press
    # https://stackoverflow.com/questions/28071750/redirecting-a-view-to-another-view-in-django-python - how to redirect in django via url pattern
    user = request.user # get db information of current user
    author = get_object_or_404(AuthorUser, uuid=uuid) # get db information of author to follow

    user_data = { # user fields put in dictionary to be added to json
        'type': user.type,
        'id': user.url,
        'uuid': user.uuid,
        'displayName': user.username,
        'host': user.host,
        'url': user.url,
        'github': user.github,
        'profileImage': user.profile_image
    }

    author_data = {# author put in dictionary to follow fields to be added to json
        'type': author.type,
        'id': author.url,
        'uuid': author.uuid,
        'displayName': author.username,
        'host': author.host,
        'url': author.url,
        'github': author.github,
        'profileImage': author.profile_image,
    }

    # create FollowRequest instance in db
    FollowRequests.objects.get_or_create(
        summary="{} wants to follow {}".format(user.username, author.username),
        requester=user_data,
        recipient=author_data,
        requester_uuid=user_data.get('uuid'),
        recipient_uuid=author_data.get('uuid')
    )

    return redirect('author_profile', uuid=uuid)


    """ 
    # proper way of serializing; doesn't seem to be an option to only choose just some of the fields
    #https://stackoverflow.com/questions/757022/how-do-you-serialize-a-model-instance-in-django - how to serialize stuff
    #https://stackoverflow.com/questions/60376352/why-there-is-like-bunch-of-backslash-in-my-json-output - how to fix the backslashes everywhere
    author_json = serializers.serialize("json", [AuthorUser.objects.get(id=uuid)])
    author_json = json.loads(author_json)
    """

def accept_fq(self, uuid, fq_uuid): # add requester to user's followers and delete friend request
    fq = FollowRequests.objects.get(requester_uuid=fq_uuid, recipient_uuid=uuid)
    requester_information = fq.requester
    author_information = AuthorUser.objects.get(uuid=uuid)
    
    # add requester to user's follower's
    obj, created = Followers.objects.get_or_create(author=author_information)

    if created: # first follower, add json of requester inside a list for future followers
        obj.followers = [requester_information]
        obj.save()

    elif (not created): # user already has followers, append requester's information to list
        obj.followers.append(requester_information) # NOTE: there is no guard against adding the same user twice, but the "Follow" button will be disabled
        obj.save()                                  # while a user is in an author's followers list. So it should be impossible for them to send another request.
        
    fq.delete()
    return redirect('author_requests', uuid=uuid) # redirect back to friend request page when finished

def deny_fq(self, uuid, fq_uuid): # delete friend request; remove the request from FriendRequests table
    fq = FollowRequests.objects.get(requester_uuid=fq_uuid, recipient_uuid=uuid) # https://stackoverflow.com/questions/3805958/how-to-delete-a-record-in-django-models how to delete objects from db
    fq.delete()
    return redirect('author_requests', uuid=uuid) # redirect back to friend request page when finished

def unfollow_author(request, uuid, rq_uuid): # unfollow an author (where uuid is the author to unfollow, and rq_uuid is the uuid of the requester to unfollow)
    followers_instance = Followers.objects.get(author=uuid) # get followers instance of author
    for follower in followers_instance.followers:
        if (follower['id'] == rq_uuid): # if the id of the follower matches that of the requester, delete this follower
            followers_instance.followers.remove(follower)
            followers_instance.save()
            break # finished
    
    return redirect('author_profile', uuid=uuid) # redirect back to author's profile page when finished

def view_my_profile(request): #TODO OBSOLETE; REMOVE? 
    user = request.user # get db information of current user
    author_obj = get_object_or_404(AuthorUser, username=user) # get db information of author to follow
    author_dict = model_to_dict(author_obj)
    return redirect('author_profile', uuid=author_dict.get("uuid"))



# API SECTION
# ===================================================================================================

def get_follower_info(request):
    follower_dict = {"type": "author",
        "id": request.data.get("id"),
        "host": request.data.get("host"),
        "username": request.data.get("displayName"),
        "url": request.data.get("url"),
        "github": request.data.get("github"),
        "profile_image": request.data.get("profileImage")}
    
    return follower_dict



# API CALLS
# ================================================================================================================================



# SINGLE AUTHOR
# =====================
@swagger_auto_schema(
    method='get',
    tags=['authors', 'remote'],
    operation_description="Retrieves the profile of a single author.",
    manual_parameters=[
            openapi.Parameter('uuid', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the author."),
        ],
    responses={
        200: AuthorUserSerializer,
        404: openapi.Response("The provided author does not exist."),
    }
)
@swagger_auto_schema(
    method='post',
    tags=['authors'],
    request_body=AuthorDetailSerializer
    )
@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_single_author(request, uuid):
    if request.method == "GET":
        author = get_object_or_404(AuthorUser, uuid=uuid)
        serializer = AuthorUserSerializer(author, many=False)
        return Response(serializer.data)
    elif request.method == "POST":
        if not request.user.is_authenticated or request.user.uuid != uuid:
            return Response(status=401, data="Unauthorized.")
        
        author = get_object_or_404(AuthorUser, uuid=uuid)
        serializer = AuthorUserSerializer(author, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.update(author, serializer.validated_data)
            return Response(serializer.data)

        return Response(status=400, data=serializer.errors)



# AUTHOR LIST 
# =====================
@swagger_auto_schema(
    method='get',
    tags=['authors', 'remote'],
    operation_description="Retrieves all profiles on the server (paginated). Example query: GET ://service/authors?page=10&size=5",
    manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Page number"),
            openapi.Parameter('size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Number of profiles per page"),
        ],
    responses={
        200: ResponseAuthorsSerializer,
    }
)
@api_view(['GET'])
def api_all_authors(request):
    # check query params for pagination

    if not request.user.is_authenticated:
        return Response(status=401, data="You must be logged in to view all authors")

    page = request.GET.get("page")
    size = request.GET.get("size")
    authors = AuthorUser.objects.all()
    
    # if pagination specified, return only the requested range
    if page is not None and size is not None:
        start = (int(page) - 1) * int(size)
        end = start + int(size)
        authors = authors[start:end]

    serializer = AuthorUserSerializer(authors, many=True)
    response = {"type": "authors", "items": serializer.data}
    return Response(response)



# FOLLOW LIST
# =====================
@swagger_auto_schema(
    method='get',
    tags=['followers', 'remote'],
    operation_description="Get the list of followers for the provided author ID.",
    manual_parameters=[
            openapi.Parameter('uuid', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the author."),
        ],
    responses={
            200: ResponseFollowersSerializer,
            404: openapi.Response("The provided author does not exist."),
        }
)
@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_follow_list(request, uuid):
    author = get_object_or_404(AuthorUser, uuid=uuid)
    try: 
        followers = Followers.objects.get(author=author)
        formatted = []
        for follower in followers:
            ad = AuthorDetail()
            ad.setMapping(follower)
            formatted.append(ad.formatAuthorInfo())

        serializer = AuthorDetailSerializer(data=formatted, many=True)
        if not serializer.is_valid():
            return Response(status=500, data="Server Error")
        
        return {"type": "followers", "items": serializer.data}
    # case if author has no followers yet
    except Followers.DoesNotExist:
        response = {"type": "followers", "items": []}
    except:
        return Response(status=500, data="Something went wrong")
    
    return Response(response)



# FOREIGN FOLLOWER
# =====================
@swagger_auto_schema(
    method='get',
    tags=['followers', 'remote'],
    operation_description="Checks if the foreign author is a follower of the author.",
    manual_parameters=[
            openapi.Parameter('uuid', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the author in check."),
            openapi.Parameter('foreign_author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the foreign author."),
        ],
    responses={
            200: openapi.Response("The foreign author is a follower of the author."),
            404: openapi.Response("The foreign author is not following the author."),
        }
)
@swagger_auto_schema(
    methods=['put', 'delete'],
    tags=['followers']
)
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_foreign_follower(request, uuid, foreign_author_id):
    author = get_object_or_404(AuthorUser, uuid=uuid)
    noFollowers = False
    index = -1

    # first determine if foreign_author_id is in author's followers list
    try:
        followers = Followers.objects.get(author=author)

        for f in range(len(followers.followers)):
            if followers.followers[f]['uuid'] == foreign_author_id:
                index = f
    
        found = index != -1

    except Followers.DoesNotExist:
        noFollowers = True
        found = False
    except:
        return Response(status=500, data="Something went wrong")
            
    if request.method == "GET":
        # return 200 if found, 404 if not found
        if found:
            return Response(status=200, data="OK")
        else:
            return Response(status=404, data="Not found")
    
    # TODO: TEST
    elif request.method == "PUT":
        # this is expecting the request body to be the json of the follower, as per the spec

        if not request.user.is_authenticated:
            return Response(status=401, data="You must be logged in to follow someone")
        
        if found:
            return Response(status=400, data="You are already following this user")
        
        new_follower = get_follower_info(request)
        serializer = FollowerSerializer(data=new_follower, partial=True)

        if not serializer.is_valid():
            return Response(status=400, data=serializer.errors)
        
        new_follower = serializer.validated_data
        if noFollowers:
            followers = Followers.objects.create(author=author, followers=[new_follower])
        else:
            followers.followers.append(new_follower)

        followers.save()
        # respond with 200 and the follower json
        return Response(status=200, data=new_follower)
        
    elif request.method == "DELETE":
        if not request.user.is_authenticated:
            return Response(status=401, data="You must be logged in to unfollow someone")
        
        if not found:
            return Response(status=400, data="You are not following this user")
        
        follower = followers.followers[index]
        followers.followers.pop(index)
        followers.save()
        return Response(status=200, data=follower)



# FOLLOW REQUESTS
# =====================
@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_follow_requests(request):
    if request.method == "GET":
        follow_requests = FollowRequests.objects.all()
        serializer = FollowRequestsSerializer(follow_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "POST":
        serializer = FollowRequestsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

