import json
import enum
from venv import create
from django.http import HttpResponse

from django.forms.models import model_to_dict
from django.views.generic import TemplateView, ListView, DetailView
from accounts.models import AuthorUser, FollowRequests, Followers

# wip
from django.core import serializers
from django.shortcuts import get_object_or_404, redirect, render 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .seralizers import AuthorUserSerializer, FollowerSerializer, FollowerListSerializer

# DFB pg. 60
def home_page_view(request): # basic generic view that just displays template
    if (request.user.is_authenticated): # if user is logged in, immediately redirect to posts stream
        return redirect('stream')
    
    return render(request, 'home.html') # otherwise they're not logged in, and should be prompted with the homepage to login or signup

class ListProfilesView(ListView): # basic generic view that just displays template
    model = AuthorUser
    template_name = "listprofiles.html" 
    context_object_name = 'authors_list'

class AuthorDetailView(DetailView): # basic generic view that just displays template
    model = AuthorUser
    template_name = "authorprofile.html" 
    context_object_name = 'author'

def author_user_detail(request, pk):
    author_user = AuthorUser.objects.get(pk=pk)
    try: # author to be viewed has at least one follower
        followers = Followers.objects.get(author=author_user)
        num_followers = len(followers.followers)
        viewing_user = request.user.username
        already_following = False

        for i in range(0, num_followers):
            #print(followers.followers[i]['username']) # debug
            if (followers.followers[i]['username'] == viewing_user): # if the the viewing/logged in user is in the viewed author's followers list, hide follow button
                already_following = True
    except: # author to be viewed has no followers (no instance in db yet)
        already_following = False
        followers = None # safe?

    # followers.followers[0]['username']

    
    #for (element in followers.followers):
        #print(elements)
        

    return render(request, 'authorprofile.html', {'author': author_user, 'followers': followers, 'already_following': already_following})

class FollowRequestsListView(LoginRequiredMixin, UserPassesTestMixin, ListView): # basic generic view that just displays template
    model = FollowRequests
    template_name = "followrequests.html" 
    context_object_name = 'requests_list'

    def test_func(self): # CHATGPT - 2023-10-30 Prompt #1
        user_id = self.kwargs.get('pk')  # Assuming 'pk' is the user ID in the URL.
        return self.request.user.id == user_id

    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have permission to access this page.")

    

def follow_author(request, pk): # CHATGPT - 2023-10-20 Prompt #1
    # https://stackoverflow.com/questions/74199737/how-to-create-django-model-by-pressing-button - general structure followed for how to create a model instance in db via button press
    # https://stackoverflow.com/questions/28071750/redirecting-a-view-to-another-view-in-django-python - how to redirect in django via url pattern
    user = request.user # get db information of current user
    author = get_object_or_404(AuthorUser, pk=pk) # get db information of author to follow

    user_data = { # user fields put in dictionary to be added to json
        'type': user.type,
        'id': user.id,
        'username': user.username,
        'host': user.host,
        'url': user.url,
        'github': user.github,
        'profile_image': user.profile_image
    }

    author_data = {# author put in dictionary to follow fields to be added to json
        'type': author.type,
        'id': author.id,
        'username': author.username,
        'host': author.host,
        'url': author.url,
        'github': author.github,
        'profile_image': author.profile_image,
    }

    # create FollowRequest instance in db
    FollowRequests.objects.get_or_create(
        summary="{} wants to follow {}".format(user.username, author.username),
        requester=user_data,
        recipient=author_data
    )

    return redirect('author_profile', pk=pk)


    """ 
    # proper way of serializing; doesn't seem to be an option to only choose just some of the fields
    #https://stackoverflow.com/questions/757022/how-do-you-serialize-a-model-instance-in-django - how to serialize stuff
    #https://stackoverflow.com/questions/60376352/why-there-is-like-bunch-of-backslash-in-my-json-output - how to fix the backslashes everywhere
    author_json = serializers.serialize("json", [AuthorUser.objects.get(id=pk)])
    author_json = json.loads(author_json)
    """

def accept_fq(self, pk, fq_pk): # add requester to user's followers and delete friend request
    fq = FollowRequests.objects.get(id=fq_pk)
    requester_information = fq.requester
    author_information = AuthorUser.objects.get(pk=pk)
    
    # add requester to user's follower's
    obj, created = Followers.objects.get_or_create(author=author_information)

    if created: # first follower, add json of requester inside a list for future followers
        obj.followers = [requester_information]
        obj.save()

    elif (not created): # user already has followers, append requester's information to list
        obj.followers.append(requester_information) # NOTE: there is no guard against adding the same user twice, but the "Follow" button will be disabled
        obj.save()                                  # while a user is in an author's followers list. So it should be impossible for them to send another request.
        
    fq = FollowRequests.objects.get(id=fq_pk)
    fq.delete()
    return redirect('author_requests', pk=pk) # redirect back to friend request page when finished

def deny_fq(self, pk, fq_pk): # delete friend request; remove the request from FriendRequests table
    fq = FollowRequests.objects.get(id=fq_pk) # https://stackoverflow.com/questions/3805958/how-to-delete-a-record-in-django-models how to delete objects from db
    fq.delete()
    return redirect('author_requests', pk=pk) # redirect back to friend request page when finished

def view_my_profile(request):
    user = request.user # get db information of current user
    author_obj = get_object_or_404(AuthorUser, username=user) # get db information of author to follow
    author_dict = model_to_dict(author_obj)
    return redirect('author_profile', pk=author_dict.get("id"))



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

@api_view(['GET', 'POST'])
def api_single_author(request, pk):
    if request.method == "GET":
        author = get_object_or_404(AuthorUser, pk=pk)
        serializer = AuthorUserSerializer(author, many=False)
        return Response(serializer.data)
    elif request.method == "POST":
        author = get_object_or_404(AuthorUser, pk=pk)
        serializer = AuthorUserSerializer(author, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.update(author, serializer.validated_data)
            return Response(serializer.data)

        return Response(status=400, data=serializer.errors)

@api_view(['GET'])
def api_all_authors(request):
    # check query params for pagination
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

@api_view(['GET'])
def api_follow_list(request, pk):
    author = get_object_or_404(AuthorUser, pk=pk)
    try: 
        followers = Followers.objects.get(author=author)
        serializer = FollowerSerializer(followers.followers, many=True)
        response = {"type": "followers", "items": serializer.data}
    # case if author has no followers yet
    except Followers.DoesNotExist:
        response = {"type": "followers", "items": []}
    except:
        return Response(status=500, data="Something went wrong")
    
    return Response(response)

@api_view(['GET', 'PUT', 'DELETE'])
def api_foreign_follower(request, pk, foreign_author_id):
    author = get_object_or_404(AuthorUser, pk=pk)
    noFollowers = False
    index = -1

    # first determine if foreign_author_id is in author's followers list
    try:
        followers = Followers.objects.get(author=author)

        for f in range(len(followers.followers)):
            if followers.followers[f]['id'] == foreign_author_id:
                index = f
    
        found = index != -1

    except Followers.DoesNotExist:
        noFollowers = True
    except:
        return Response(status=500, data="Something went wrong")
            
    if request.method == "GET":
        # return 200 if found, 404 if not found
        if found:
            return Response(status=200, data="OK")
        else:
            return Response(status=404, data="Not found")
        
    elif request.method == "PUT":
        # this is expecting the request body to be the json of the follower, as per the spec

        if not request.user.is_authenticated:
            return Response(status=401, data="You must be logged in to follow someone")
        
        if found:
            return Response(status=400, data="You are already following this user")
        
        new_follower = get_follower_info(request)

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