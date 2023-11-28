import json
from django.http import HttpResponse

from django.forms.models import model_to_dict
from django.views.generic import TemplateView, ListView, DetailView
from accounts.models import AuthorUser, FollowRequests, Followers

# wip
from django.shortcuts import get_object_or_404, redirect, render 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from connections.caches import AuthorCache, Nodes


from util import AuthorDetail
from .seralizers import AuthorDetailSerializer, AuthorUserSerializer, FollowRequestsSerializer, FollowerListSerializer, AuthorUserReferenceSerializer, ResponseAuthorsSerializer, ResponseFollowersSerializer
from static.vars import ENDPOINT, HOSTS
from util import get_id_from_url
import requests
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from requests.auth import HTTPBasicAuth

# RENDERING VIEWS
# ================================================================================================================================

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
# ------------------------
# new implementation, acquiring profiles from all connected hosts including local
def list_profiles(request):
    # the api url to get list of profiles
    url = "/authors/"
    all_authors = []
    nodes = Nodes()

    search_text=""
    usernames_found=""
    
    searchbar_is_used=False

    if request.method == "POST":#if the search bar is used
        search_text=request.POST['search_bar']#get the string from the search bar
        searchbar_is_used=True

    author_cache = AuthorCache()
    toReturn = []

    if searchbar_is_used == True:
        for author in author_cache.values():
            if author["displayName"].find(search_text) > -1:
                toReturn.append(author)
    else:
        toReturn = author_cache.values()
    
    return render(request, 'listprofiles.html', {'authors_list': toReturn, 'search_text':search_text})


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
# ----------------------

def get_author_detail(request):

    author_detail_url = request.POST.get("get_url")
    plain_id = get_id_from_url(author_detail_url)

    host = request.POST.get("host")
    host = host[:-1] if host[-1] == "/" else host
    index = HOSTS.index(host)

    return HttpResponse(content=json.dumps({"host_index":index, "uuid": plain_id}))


def render_author_detail(request, host_id, uuid):
    # grab the author information

    gathered_all_info = True

    nodes = Nodes()
    auth = nodes.get_auth_for_host(HOSTS[host_id])
    headers = {"Accept": "application/json"}
    url = nodes.get_host_for_index(host_id)

    try:
        if host_id == 1:
            headers["Referer"] = nodes.get_host_for_index(0)

        path = url + "/authors/" + uuid + "/"
        response = requests.get(path, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)

        if response.ok:
            author = response.json()
            # already validated from the originating view, so do not have to check for serialization
            author["uuid"] = uuid
        else:
            # TODO render and error page
            return HttpResponse(content="Author not found", status=response.status_code)
    except:
        # TODO render and error page
        return HttpResponse(content="Author not found", status=404)

    # grab the followers information
    all_followers = []

    try:
        path = url + "/authors/" + uuid + "/followers/"     
        print(path)
        response = requests.get(path, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)
        print(response)
        if response.ok:
            followers = response.json()
            for follower in followers["items"]:
                try:
                    # serialize to check if everything is in expected format
                    serializer = AuthorDetailSerializer(data=follower)
                    # exclude if invalid
                    if not serializer.is_valid():
                        continue
                    # assign uuid from full url
                    valid_follower = serializer.validated_data
                    valid_follower["uuid"] = get_id_from_url(valid_follower["url"])
                    all_followers.append(valid_follower)
                except Exception as e:
                    gathered_all_info = False
                    print(e)

    except Exception as e:
        gathered_all_info = False
        print(e)

    # check if we are following the user in view
    following = False
    try:
        path = url + "/authors/" + uuid + "/followers/" + request.user.uuid + "/"
        
        response = requests.get(path, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)
        if host_id == 0 and response.ok:
            following = True
        elif host_id == 1 and response.ok:
            following = response.json()["is_follower"]
    except:
        following = False
        gathered_all_info = False                   

    # check if we have a request for the user in view
    follow_rq = FollowRequests.objects.filter(requester_uuid=request.user.uuid , recipient_uuid=uuid)
    requested = len(follow_rq) > 0

    return render(request, 'authorprofile.html', {'author': author, 'followers': all_followers, 'already_following': following, 'pending_request': requested, 'missing_info': not gathered_all_info})


# We've switched to inbox view for this
@DeprecationWarning
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



# FUNCTIONAL URLs
# ================================================================================================================================
@DeprecationWarning
def follow_author(request, uuid): # CHATGPT - 2023-10-20 Prompt #1
    """ 
    # proper way of serializing; doesn't seem to be an option to only choose just some of the fields
    #https://stackoverflow.com/questions/757022/how-do-you-serialize-a-model-instance-in-django - how to serialize stuff
    #https://stackoverflow.com/questions/60376352/why-there-is-like-bunch-of-backslash-in-my-json-output - how to fix the backslashes everywhere
    author_json = serializers.serialize("json", [AuthorUser.objects.get(id=uuid)])
    author_json = json.loads(author_json)
    """
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

def follow_requests(request):
    user = request.user # get db information of current user
    follow_requests = FollowRequests.objects.filter(recipient_uuid=user.uuid) # get all friend requests where the user is the recipient

    requests = []
    author_cache = AuthorCache()
    for frq in follow_requests:
        requester = model_to_dict(frq)
        requester["data"] = author_cache.get(frq.requester_uuid)
        requests.append(requester)
    
    return render(request, 'followrequests.html', {'requests_list': requests})

def accept_fq(request): # add requester to user's followers and delete friend request
    requester_uuid = request.POST.get('requester_uuid') # get uuid of requester
    recipient_uuid = request.POST.get('recipient_uuid') # get uuid of recipient

    # safety
    if request.user.uuid != recipient_uuid: # if the user is not the recipient of the request, they should not be able to accept it
        return HttpResponseForbidden("You do not have permission to access this page.")

    fq = FollowRequests.objects.get(requester_uuid=requester_uuid, recipient_uuid=recipient_uuid) # get friend request instance from db
    author = AuthorUser.objects.get(uuid=recipient_uuid)

    ad = AuthorDetail(fq.requester_uuid, fq.requester_url, fq.requester_host) # create AuthorDetail object from requester information
    requester_data = ad.formMapping()
    
    # add requester to user's follower's
    obj, created = Followers.objects.get_or_create(author=author)

    if created: # first follower, add json of requester inside a list for future followers
        obj.followers = [requester_data]
        obj.save()

    elif (not created): # user already has followers, append requester's information to list
        obj.followers.append(requester_data) # NOTE: there is no guard against adding the same user twice, but the "Follow" button will be disabled
        obj.save()                                  # while a user is in an author's followers list. So it should be impossible for them to send another request.
        
    fq.delete()

    return JsonResponse({"status":"success"})


def deny_fq(request): # delete friend request; remove the request from FriendRequests table
    requester_uuid = request.POST.get('requester_uuid') # get uuid of requester
    recipient_uuid = request.POST.get('recipient_uuid') # get uuid of recipient

    # safety
    if request.user.uuid != recipient_uuid: # if the user is not the recipient of the request, they should not be able to accept it
        return HttpResponseForbidden("You do not have permission to access this page.")

    fq = FollowRequests.objects.get(requester_uuid=requester_uuid, recipient_uuid=recipient_uuid) # get friend request instance from dbfq.delete()
    fq.delete()

    return JsonResponse({"status":"success"}) # redirect back to friend request page when finished


def unfollow_author(request, uuid, rq_uuid): # unfollow an author (where uuid is the author to unfollow, and rq_uuid is the uuid of the requester to unfollow)
    followers_instance = Followers.objects.get(author=uuid) # get followers instance of author
    for follower in followers_instance.followers:
        if (follower['id'] == rq_uuid): # if the id of the follower matches that of the requester, delete this follower
            followers_instance.followers.remove(follower)
            followers_instance.save()
            break # finished
    
    return redirect('author_profile', uuid=uuid) # redirect back to author's profile page when finished



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
    author_cache = AuthorCache()
    try: 
        follow_list = Followers.objects.get(author=author)
        formatted = []
        for follower in follow_list.followers:
            formatted.append(author_cache.get(follower["uuid"]))

        response = {"type": "followers", "items": formatted}
    # case if author has no followers yet
    except Followers.DoesNotExist:
        response = {"type": "followers", "items": []}
    except Exception as e:
        print(e)
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

        if request.user.uuid != uuid:
            return Response(status=401, data="Unauthorized")
        
        if found:
            return Response(status=400, data="This user is already following you")
        
        author_cache = AuthorCache()
        follower = author_cache.get(foreign_author_id)

        ad = AuthorDetail()
        ad.setMappingFromAPI(follower)
        follower_db_data = ad.formMapping()

        if noFollowers:
            followers = Followers.objects.create(author=author, followers=[follower_db_data])
        else:
            followers.followers.append(follower_db_data)

        followers.save()
        # respond with 200 and the follower json
        return Response(status=200, data=follower)
        
    elif request.method == "DELETE":
        
        if request.user.uuid != uuid and request.user.uuid != foreign_author_id:
            return Response(status=401, data="Unauthorized")
        
        if not found:
            return Response(status=404, data="You are not following this user")
        
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

