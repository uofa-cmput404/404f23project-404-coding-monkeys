import datetime
import json
import bleach
import commonmark
from django.shortcuts import render, get_object_or_404, redirect 
from django.views.generic import CreateView
from django.forms.models import model_to_dict
import requests
from connections.caches import AuthorCache, PostCache
from pages.seralizers import AuthorUserSerializer, CommentListSerializer, CommentSerializer
from util import AuthorDetail
from util import get_id_from_url, get_part_from_url
from rest_framework.response import Response
from posts.serializers import LikeListSerializer, LocalPostsSerializer, PostsSerializer, ResponsePosts
from .models import Posts, Likes, Comments
from .forms import PostForm
from django.urls import reverse
from accounts.models import AuthorUser, Followers
import uuid
import base64
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.test import Client
from django.core.files.base import ContentFile
from PIL import Image
from drf_yasg.utils import swagger_auto_schema
from static.vars import ENDPOINT, HOSTS
from django.http import HttpResponse
from django.core.serializers import serialize
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import copy
from requests.auth import HTTPBasicAuth
from connections.caches import Nodes
from util import time_since_posted, format_local_post_from_db, format_local_post


class PostCreate(CreateView):
    model = Posts
    template_name = "posts/create.html"
    form_class = PostForm

    def get_success_url(self): # gpt
        return reverse('all')

def make_new_post(request, form=None):
    if request.method == 'GET':
        author_cache = AuthorCache()
        url = f"{ENDPOINT}/authors/{request.user.id}"
        authors = []
        for author in author_cache.values():
            if author["url"] != url:
                author["uuid"] = get_id_from_url(author["id"])
                authors.append(author)

        if form:
            return render(request, 'posts/create.html', {'form': form, 'author_list':authors})
        else:
            return render(request, 'posts/create.html', {'form': PostForm(), 'author_list':authors})
    elif request.method == 'POST':
        return update_or_create_post(request, None)
        
def get_picture_info(picture):
    image_base64 = base64.b64encode(picture.read()).decode('utf-8')

    #Determine content type:
    if picture.name.endswith(".jpg") or picture.name.endswith(".jpeg"):
        contentType_pic = "image/jpeg;base64"
    elif picture.name.endswith(".png"):
        contentType_pic = "image/png;base64"
    else:
        contentType_pic = "application/base64"
    
    return image_base64, contentType_pic

def update_or_create_post(request, post_uuid):
    author_cache = AuthorCache()

    # create or grab post first
    try:
        if post_uuid:
            post = Posts.objects.get(uuid=post_uuid)
            unique_id = post.uuid
        else:
            raise Posts.DoesNotExist()
    except Posts.DoesNotExist:
        unique_id = uuid.uuid4()
        author = get_author_info(request.user.id) # convert author object to dictionary
        post_url = f"{ENDPOINT}authors/{author['id']}/posts/{unique_id}"
        post = Posts(uuid=unique_id, author_uuid=author["id"], source=post_url, origin=post_url, author_local=1, author_host=ENDPOINT, author_url=author["url"], count=0, comments="", unlisted=False)

    unique_id_pic = str(unique_id) + "_pic"

    post.title = request.POST.get('title')
    post.description = request.POST.get('description')
    post.content = request.POST.get('content')
    post.categories = request.POST.get('categories') if request.POST.get('categories') != "" else []
    post.comments = f"{ENDPOINT}authors/{post.author_uuid}/posts/{post.uuid}/comments"
    post.visibility = request.POST.get('visibility')

    # strip html tags
    user_input = request.POST.get('content')
    bleached = bleach.clean(user_input)
    post.content = bleached

    cType = request.POST.get('contentType')
    if cType == "Text":
        post.contentType = "text/plain"
    elif cType == "Markdown":
        post.contentType = "text/markdown"
    elif cType == "Image":
        image_base64, contentType_pic = get_picture_info(request.FILES.get('picture'))
        post.contentType = contentType_pic
        post.content = image_base64

    # add images and links to content
    if request.FILES.get('picture') is not None:
        source = f"{ENDPOINT}authors/{post.author_uuid}/posts/{post.uuid}/image"
        if post.contentType == "text/plain":
            image_tag = f"<img src=\"{source}\" alt=\"{post.title}\" />"
            post.content += "\n" + image_tag
        elif post.contentType == "text/markdown":
            image_tag = f"![{post.title}]({source})"
            post.content += "\n" + image_tag

    post.save()

    post_cache = PostCache()
    post_cache.add(str(post.uuid), format_local_post(post))

    if request.POST.get('author_list') and post.visibility == "PRIVATE":
        selected_author_id = request.POST.get('author_list')
        details = author_cache.get(selected_author_id)
        ad = AuthorDetail()
        ad.setMappingFromAPI(details)

        # send to inbox
        try:
            post_url = f"{ENDPOINT}authors/{post.author_uuid}/posts/{post.uuid}"
            response = requests.get(post_url)
            if response.ok:
                payload = response.json()
                inbox_url = f"{ad.host}authors/{ad.uuid}/inbox"
                response = requests.post(inbox_url, json=payload)
        except Exception as e:
            print(e)

    elif post.visibility == "FRIENDS":
        friends = get_friends(request.user.id)
        try:
            post_url = f"{ENDPOINT}authors/{post.author_uuid}/posts/{post.uuid}"
            response = requests.get(post_url)
            if response.ok:
                payload = response.json()
        
                for friend in friends:
                    # send to inbox
                    inbox_url = f"{friend['host']}authors/{friend['id']}/inbox"
                    response = requests.post(inbox_url, json=payload)
        except Exception as e:
            print(e)

    # deal with embedded pictures
    try:
        post = Posts.objects.get(uuid=unique_id_pic)
    except Posts.DoesNotExist:
        post.uuid = unique_id_pic
        post.unlisted = True

    # update existing pic post
    if cType != "Image" and request.FILES.get('picture') is not None:
        image_base64, contentType_pic = get_picture_info(request.FILES.get('picture'))
        post.content = image_base64
        post.contentType = contentType_pic
        post.save()

    return redirect('stream')

def edit_post(request, author_id, post_uuid):
    if request.method == 'GET':
        #read the post (whose like button the user clicked) object from db
        try:
            post = Posts.objects.get(uuid=post_uuid)

            # try:
            #     pic_post = Posts.objects.get(uuid=f'{post_uuid}_pic')
            #     image_data = base64.b64decode(pic_post.content)
            #     image_file = ContentFile(image_data)
            #     image = Image.open(image_file)
            # except Posts.DoesNotExist:
            #     image = None

            form_data = {
                'uuid': post_uuid,
                'title': post.title,
                'description': post.description,
                'categories': post.categories,
                'content': post.content,
                'visibility': post.visibility,
                'picture': ''
            }

            if post.visibility == "PRIVATE":
                form_data['sharedWith'] = post.sharedWith['id']

            return make_new_post(request, PostForm(initial=form_data))
        except Posts.DoesNotExist: 
            return redirect('stream')
        
    elif request.method == 'POST':
        return update_or_create_post(request, post_uuid)

def delete_post(request, post_uuid):
    if request.method == 'GET':
        post_cache = PostCache()
        #read the post (whose like button the user clicked) object from db
        try:
            post = Posts.objects.get(uuid=post_uuid)

            post_cache.remove(str(post.uuid))
            post.delete()

            pic_post = Posts.objects.get(uuid=f'{post_uuid}_pic')
            pic_post.delete()

            return Response(status=200)

        except Posts.DoesNotExist: 
            return redirect('stream')
        
        return redirect('stream')

def get_author_info(author_id):
    author_obj = get_object_or_404(AuthorUser, id=author_id) # get db information of author to follow
    full_dict = model_to_dict(author_obj) # convert author object to dictionary
    clean_dict = {"type": "author",
                    "id": full_dict.get("uuid"),
                    "host": full_dict.get("host"),
                    "displayName": full_dict.get("username"),
                    "url": full_dict.get("url"),
                    "github": full_dict.get("github"),
                    "profileImage": full_dict.get("profile_image")}

    return clean_dict

def get_friends(author_id):
    friends = []
    # get all followers for current user
    try:
        row = Followers.objects.get(author_id=author_id)
        current_followers = row.followers
    except Followers.DoesNotExist:
        current_followers = []

    for follower in current_followers:
        try:
            request = f"{ENDPOINT}/authors/{author_id}/followers/{follower['uuid']}"
            response = requests.get(request)
            if response.ok:
                friends.append(follower)
        except:
            continue

    return friends

def determine_if_friends(current_followers : list, user_id : str, post_author_id : str):
    try:
        row = Followers.objects.get(author_id=post_author_id)
        author_followers = [follower['id'] for follower in row.followers]
    except Followers.DoesNotExist:
        author_followers = []
    
    return post_author_id in current_followers and user_id in author_followers

def post_stream(request):
    toReturn = []

    post_cache = PostCache()
    posts = post_cache.values()

    for post in posts:
        post["author_uuid"] = get_part_from_url(post["author"]["id"], "authors")
        post["uuid"] = get_part_from_url(post["id"], "posts")
        post["delta"] = time_since_posted(post["published"])

        if post["contentType"] == "text/markdown":
            post["content"] = commonmark.commonmark(post["content"])
        elif post["content"] and post["origin"].startswith(HOSTS[1]) and post["contentType"] not in ("text/plain", "text/markdown"):
            post["content"] = post["content"].split(",")[1] if len(post["content"].split(",")) == 2 else post["content"]
        toReturn.append(post)
    sorted_posts = sorted(toReturn, key=lambda x: x["published"], reverse=True)

    return render(request, 'posts/dashboard.html', {'all_posts': sorted_posts})

def update_post_with_like_count_from_API(post):
    #Takes a post object and updates the like count property based on the number of likes returned by the API
    #This will allow us to remove the likeCount field from our database (eventually)
    #Note this process is SLOW as it makes one API call per post

    #For now this only works for public posts
    if post.visibility != 'PUBLIC': return post

    nodes = Nodes() 
    endpoint_tmp = ENDPOINT
    if endpoint_tmp.endswith('/'): endpoint_tmp = endpoint_tmp[:-1] #Safety for trailing /
    linkToPost = f"{endpoint_tmp}/authors/{post.author_uuid}/posts/{post.uuid}"

    #Get list of likes from the current user
    full_url = f"{linkToPost}/likes"
    headers = {"accept": "application/json"}
    auth = nodes.get_auth_for_host(endpoint_tmp)
    try:
        response = requests.get(full_url, headers=headers, auth=HTTPBasicAuth(auth[0], auth[1]))
    except:
        print(f"Error: Could not get likes for post with UUID: {post.uuid}")
        post.likeCount = 0
        return post
    
    if not response.ok: print(f"API error when gathering list of likes for post with UUID: {post.uuid}")
    returned_likes = response.json()

    post.likeCount = len(returned_likes["items"])

    return post

def view_posts(request):
    author_id = request.user.uuid
    viewable = []
    determined_friends = set()
    # exclude picture posts since they're dealt with in the html template
    posts = Posts.objects.order_by('-published')

    try:
        row = Followers.objects.get(author_id=author_id)
        current_followers = [follower['uuid'] for follower in row.followers]
    except Followers.DoesNotExist:
        current_followers = []

    for post in posts:
        if post.visibility == "PUBLIC":
            viewable.append(post)

        # show own posts
        elif post.author_uuid == author_id:
            viewable.append(post)

        elif post.visibility == "FRIENDS":
            if post.author_uuid in determined_friends or determine_if_friends(current_followers, author_id, post.author['id']):
                viewable.append(post)
                determined_friends.add(post.author['id'])

        elif post.visibility == "PRIVATE":
            sharedIDs = [author["uuid"] for author in post.sharedWith]
            if author_id in sharedIDs:
                viewable.append(post)

    formatted = []
    for post in viewable:
        if post.contentType == "text/markdown":
            post.content = commonmark.commonmark(post.content)
        post_data = format_local_post_from_db(post)
        formatted.append(post_data)

    return render(request, 'posts/dashboard.html', {'all_posts': formatted})

def open_comments_handler(request):
    nodes = Nodes()

    #Get the post object from the front end
    post = json.loads(request.body).get('post', {})

    #gather the host of the post
    post_host = post['author']['host']
    if post_host.endswith('/'): post_host = post_host[:-1] #Safety for trailing /

    if post_host == "http://127.0.0.1:8000" or post_host == "https://chimp-chat-1e0cca1cc8ce.herokuapp.com":
        #API call for calling code Monkeys
        full_url = f"{post_host}/authors/{post['author_uuid']}/posts/{post['uuid']}/comments/"
        headers = {
            "accept": "application/json",
        }
        params = {
            "page": 1,
            "size": 10
        }
        auth = nodes.get_auth_for_host(post_host)
        response = requests.get(full_url, headers=headers, auth=HTTPBasicAuth(auth[0], auth[1]), params=params)
    elif post_host == "https://distributed-network-37d054f03cf4.herokuapp.com":
        #API call for 404 Team not found
        full_url = f"{post_host}/api/authors/{post['author_uuid']}/posts/{post['uuid']}/comments/"
        headers = {
            "Referer": "https://chimp-chat-1e0cca1cc8ce.herokuapp.com/",
            "accept": "application/json",
        }
        auth = nodes.get_auth_for_host(post_host)
        response = requests.get(full_url, headers=headers, auth=HTTPBasicAuth(auth[0], auth[1]))


    if not response.ok: print(f"API error when gathering comments for post with UUID: {post['uuid']}")
    returned_comments = response.json()

    formatted = []
    for comment in returned_comments['comments']:
        formatted.append(comment)

    return JsonResponse({'comments': json.dumps(formatted)})

def submit_comment_handler(request):
    nodes = Nodes()

    post = json.loads(request.body).get('post', {})
    post_host = post['author']['host']
    if post_host.endswith('/'): post_host = post_host[:-1] #Safety for trailing /

    print(json.dumps(post, indent=2))

    commentText = json.loads(request.body).get('comment_text', {})

    #Get current user info
    currUser = AuthorUser.objects.get(uuid=request.user.uuid) #get the current user
    currUser_API = get_API_formatted_author_dict_from_author_obj(currUser) #format user details for API usage

    if post_host == "http://127.0.0.1:8000" or post_host == "https://chimp-chat-1e0cca1cc8ce.herokuapp.com":
        #send comment
        full_url = f"{post_host}/authors/{post['author_uuid']}/posts/{post['uuid']}/comments/"
        headers = {"Content-Type": "application/json"}
        auth = nodes.get_auth_for_host(post_host)
        comment_details = {
            "type": "comment",
            "author": currUser_API,
            "comment": commentText,
            "contentType": "text/plain",
            "published": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00'),
            "id": f"{post_host}/authors/{post['author_uuid']}/posts/{post['uuid']}/comments/{uuid.uuid4()}"
        }
        comment_details_json = json.dumps(comment_details)
        # print(f"\nAPI Call for Sending Like Obj:\nURL: {full_url}\nHeaders: {headers}\nAuth: {auth}\nBody:\n{json.dumps(body_dict, indent=2)}") #Debug the API call
        response = requests.post(full_url, headers=headers, auth=HTTPBasicAuth(auth[0], auth[1]), data=comment_details_json) #Send the like object to the posting author's inbox

    elif post_host == "https://distributed-network-37d054f03cf4.herokuapp.com":
        #send comment
        full_url = f"{post_host}/api/authors/{post['author_uuid']}/posts/{post['uuid']}/comments/"
        headers = {
            "Referer": "https://chimp-chat-1e0cca1cc8ce.herokuapp.com/",
            "accept": "application/json",
            'Content-Type': 'application/json'
        }
        auth = nodes.get_auth_for_host(post_host)
        comment_details = {
            "type": "comment",
            "author": currUser_API,
            "comment": commentText,
            "contentType": "text/plain",
            "published": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00'),
            "id": f"{post_host}/authors/{post['author_uuid']}/posts/{post['uuid']}/comments/{uuid.uuid4()}"
        }
        comment_details_json = json.dumps(comment_details)
        # print(f"\nAPI Call for Sending Comment Obj:\nURL: {full_url}\nHeaders: {headers}\nAuth: {auth}\nData:\n{json.dumps(comment_details, indent=2)}") #Debug the API call
        response = requests.post(full_url, headers=headers, auth=HTTPBasicAuth(auth[0], auth[1]), data=comment_details_json) #Send the like object to the posting author's inbox
    
    if not response.ok: print(f"API error when adding new comment")
    return JsonResponse({'comments': json.dumps([comment_details])})

def get_object_type(url):
    sections = url.split("/")
    return "post" if sections[-2] == "posts" else "comment"

def get_API_formatted_author_dict_from_author_obj(authorObj):
    formatted_dict = {
        "type": "author",
        "id": authorObj.url,
        "host": authorObj.host,
        "displayName": authorObj.username,
        "url": authorObj.url,
        "github": authorObj.github,
        "profileImage": authorObj.profile_image
    }

    return formatted_dict

def single_posts(request):
  post = Posts.objects.order_by('-published').first()
  post = update_post_with_like_count_from_API(post) #This replaces the likeCount value from the database with a value from the api. Note, this is SLOW (One api call per post)
  post_data = format_local_post_from_db(post)

  return render(request, "single_unlisted_post.html", {"post": post_data})

def like_post_handler(request):
    nodes = Nodes()

    #Get the post object from the front end
    post = json.loads(request.body).get('post', {})

    #gather the host of the post
    post_host = post['author']['host']
    if post_host.endswith('/'): post_host = post_host[:-1] #Safety for trailing /

    #Get current user info
    currUser = AuthorUser.objects.get(uuid=request.user.uuid) #get the current user
    currUser_API = get_API_formatted_author_dict_from_author_obj(currUser) #format user details for API usage

    #Get list of likes from the current user
    full_url = f"{post_host}/authors/{currUser.uuid}/liked/"
    headers = {"accept": "application/json"}
    auth = nodes.get_auth_for_host(post_host)
    # print(f"\nAPI Call for Getting Likes:\nURL: {full_url}\nHeaders: {headers}\nAuth: {auth}") #Debug the API call
    response = requests.get(full_url, headers=headers, auth=HTTPBasicAuth(auth[0], auth[1]))
    if not response.ok: print(f"API error when gathering list of likes for user {currUser.username}")
    returned_likes = response.json()
    
    #Determine if the current user has already liked the post
    post_already_liked = False
    for like in returned_likes["items"]:
        if like['object'] == post['id']:
            post_already_liked = True
            break

    if post_already_liked:
        #dont do anything
        # return JsonResponse({'new_post_count': post['likeCount']}) #return existing post count
        return JsonResponse({'new_post_count': post['likeCount']}) #return new post count
    else:
        #send like
        full_url = f"{post_host}/authors/{currUser.uuid}/inbox/"
        headers = {"Content-Type": "application/json"}
        auth = nodes.get_auth_for_host(post_host)
        body_dict = {
            "context": "https://www.w3.org/ns/activitystreams",
            "summary": f"{currUser.username} Likes your post",
            "type": "Like",
            "author": currUser_API,
            "object": post['id']
        }
        body_json = json.dumps(body_dict)
        # print(f"\nAPI Call for Sending Like Obj:\nURL: {full_url}\nHeaders: {headers}\nAuth: {auth}\nBody:\n{json.dumps(body_dict, indent=2)}") #Debug the API call
        response = requests.post(full_url, headers=headers, auth=HTTPBasicAuth(auth[0], auth[1]), data=body_json) #Send the like object to the posting author's inbox
        if not response.ok: print(f"API error when sending like object to {post['author']['displayName']}'s inbox")

        return JsonResponse({'new_post_count': post['likeCount'] +1 }) #return new post count

def test(request):
    return render(request, 'posts/test.html')

def unlisted_post(request, author_uuid, post_uuid):
    post = Posts.objects.get(uuid=post_uuid)
    post_data = format_local_post_from_db(post)

    return render(request, 'single_unlisted_post.html', {"post": post_data})

@api_view(['GET'])
def serve_image(request, uuid, post_id):
    unique_id_pic = str(post_id) + "_pic"
    author = get_object_or_404(AuthorUser, uuid=uuid)
    pic_post = get_object_or_404(Posts, uuid=unique_id_pic, author_uuid=uuid)

    if pic_post.visibility != "PUBLIC":
        return HttpResponse(status=404)

    content_type = pic_post.contentType.split(";")[0]

    try:
        # Set the appropriate content type for the image
        pic_bytes = base64.b64decode(pic_post.content)
        response = HttpResponse(content_type=content_type)
        response.write(pic_bytes)
        return response
        # return render(request, "posts/image.html", {"image_base64": pic_post.content})
    except Exception as e:
        return HttpResponse(status=500)


# API CALLS
# ===============================================================================================================

# CUSTOM - PUBLIC POSTS
# =====================
@swagger_auto_schema(
    tags=['posts', 'remote'],
    method='get',
    operation_description="Retrieves all public posts (paginated).",
    manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Page number"),
            openapi.Parameter('size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Number of posts per page"),
        ],
    responses={
        200: ResponsePosts,
        404: openapi.Response("No post found for the provided author and post ID."),
    }
)
@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def public_posts(request):
    page = request.GET.get('page')
    size = request.GET.get('size')
    posts = Posts.objects.filter(visibility="PUBLIC").order_by('-published')

    if page and size:
        posts = posts[(int(page)-1)*int(size):int(page)*int(size)]

    formatted = []
    for post in posts:
        post_data = format_local_post_from_db(post)
        formatted.append(post_data)

    return Response({"type":"posts", "items":formatted})

# POSTS
# =====================
@swagger_auto_schema(
    tags=['posts', 'remote'],
    method='get',
    operation_description="Retrieves the public post by the author.",
    manual_parameters=[
            openapi.Parameter('uuid', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the author."),
            openapi.Parameter('post_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the post."),
        ],
    responses={
        200: PostsSerializer,
        404: openapi.Response("No post found for the provided author and post ID."),
    }
)
@swagger_auto_schema(
    tags=['posts'],
    methods=['post', 'put'],
    request_body=PostsSerializer
)
@swagger_auto_schema(
    tags=['posts'],
    methods=['delete'],
)
@api_view(['GET', 'POST', 'DELETE', 'PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_posts(request, uuid, post_id):
    if request.method == 'PUT':
        post = Posts.objects.create(uuid=post_id, author_uuid=uuid)
    else:
        post = get_object_or_404(Posts, uuid=post_id, author_uuid=uuid)

    try:
        unique_id_pic = str(post_id) + "_pic"
        pic_post = Posts.objects.get(uuid=unique_id_pic)
    except Posts.DoesNotExist:
        pic_post = None

    if request.method == 'GET':

        if post.visibility != "PUBLIC":
            return Response(status=404)
        
        post_data = format_local_post(post)
        
        serializer = PostsSerializer(data=post_data, partial=True)
        
        if not serializer.is_valid():
            return Response(status=500, data=serializer.errors)

        return Response(serializer.validated_data)

    elif request.method == 'POST':
        if not request.user.uuid != uuid:
            return Response(status=401, data="Unauthorized")
        
        serializer = PostsSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            post_data = copy.deepcopy(dict(serializer.validated_data))
            author = post_data.pop("author")
            post_data["author_uuid"] = get_id_from_url(author.get("id"))
            post_data["author_local"] = author.get("host") == ENDPOINT
            post_data["author_url"] = author.get("url")
            post_data["author_host"] = author.get("host")

            for extra in ("type","id"):
                post_data.pop(extra)

            Posts.objects.filter(uuid=post.uuid).update(**post_data)
            return Response(serializer.validated_data)

        return Response(status=400, data=serializer.errors)
    
    elif request.method == 'DELETE':
        post.delete()
        if pic_post:
            pic_post.delete()

        return Response(status=204)

    elif request.method == 'PUT':
        serializer = PostsSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.update(post, serializer.validated_data)
            return Response(serializer.data)
        
        return Response(status=400, data=serializer.errors)


# IMAGE POST
# =====================
@swagger_auto_schema(
    method='get',
    tags=['posts'],
    operation_description="Retrieves the binary of the image for the post, if one exists.",
    manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the author."),
            openapi.Parameter('post_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the post."),
        ],
    responses={
        200: openapi.Response("Returns the base-64 encoded representation of the image -- not within a JSON object for direct access. Use the `content-type` header to determine the image type."),
        404: openapi.Response("An image does not exist for the provided author and post IDs."),
    }
)
@swagger_auto_schema(
    methods=['post', 'delete', 'put'],
    auto_schema=None,
)
@api_view(['GET', 'POST', 'DELETE', 'PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_image_post(request, author_id, post_id):
    
    unique_id_pic = str(post_id) + "_pic"
    pic_post = get_object_or_404(Posts, uuid=unique_id_pic, author_uuid=author_id)

    if request.method == 'GET':
        try:
            # Set the appropriate content type for the image
            return HttpResponse(pic_post.content, content_type=pic_post.contentType)
        except Exception as e:
            return HttpResponse(status=500)
        
    elif request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Set the author of the post
            # Logic for handling multiple image uploads
            image_files = request.FILES.getlist('pictures')  # Assuming 'pictures' is the field name for image uploads

            for image_file in image_files:
                image_data, content_type = get_picture_info(image_file)
                # Save each additional picture as a separate post with the same UUID followed by '_pic' for identification
                pic_post = Posts(uuid=str(post_id) + "_pic", author=post.author, content=image_data, contentType=content_type, unlisted=True)
                pic_post.save()

            post.save()  # Save the post

            # Return a success response
            return JsonResponse({'message': 'Post created successfully'}, status=201)
    elif request.method == 'DELETE':
        try:
            image_id = request.data.get('image_id')  # Assuming 'image_id' is the identifier for the image selected
            pic_post = Posts.objects.get(uuid=str(post_id) + "_pic", id=image_id)
            pic_post.delete()  # Delete the selected image post

            
            return JsonResponse({'message': 'Image deleted successfully'}, status=200)

        except Posts.DoesNotExist:
            return JsonResponse({'error': 'Image not found'}, status=404)
    elif request.method == 'PUT':
        try:
            image_id = request.data.get('image_id')  # Assuming 'image_id' is the identifier for the image to be replaced
            pic_post = Posts.objects.get(uuid=str(post_id) + "_pic", id=image_id)

            # Update the selected image with the new image data
            image_file = request.FILES.get('new_image')  # Assuming 'new_image' is the field name for the new image upload
            if image_file:
                image_data, content_type = get_picture_info(image_file)
                pic_post.content = image_data
                pic_post.contentType = content_type
                pic_post.save()
                
                return JsonResponse({'message': 'Image updated successfully'}, status=200)

            else:
                
                return JsonResponse({'error': 'No new image provided'}, status=400)

        except Posts.DoesNotExist:
            return JsonResponse({'error': 'Image not found'}, status=404)


# POST CREATION
# =====================
@swagger_auto_schema(
    tags=['posts', 'remote'],
    method='get',
    operation_description="Retrieves the public posts by the author (paginated).",
    manual_parameters=[
            openapi.Parameter('uuid', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the author."),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Page number"),
            openapi.Parameter('size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Number of posts per page"),
        ],
    responses={
        200: ResponsePosts,
        404: openapi.Response("Author not found."),
    }
)
@swagger_auto_schema(
    tags=['posts'],
    method='post',
    request_body=PostsSerializer
)
@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_post_creation(request, uuid):
    if request.method == 'GET':
        # check query params for pagination
        get_object_or_404(AuthorUser, uuid=uuid)

        page = request.GET.get("page")
        size = request.GET.get("size")
        posts = Posts.objects.filter(author_uuid=uuid, visibility='PUBLIC').order_by('-published')

        # if pagination specified, return only the requested range
        if page is not None and size is not None:
            start = (int(page) - 1) * int(size)
            end = start + int(size)
            posts = posts[start:end]

        formatted = []
        for post in posts:
            if post.uuid.endswith("_pic"):
                continue
            formatted.append(format_local_post(post))

        serializer = PostsSerializer(posts, data=formatted, many=True, partial=True)

        if not serializer.is_valid():
            return Response(status=500, data=serializer.errors)
        
        response = {"type": "posts", "items": serializer.validated_data}
        return Response(response)
    elif request.method == 'POST':
        pass



# COMMENTS
# =====================
@swagger_auto_schema(
    tags=['comments', 'remote'],
    method='get',
    operation_description="Retrieves the list of comments for a public post (paginated).",
    manual_parameters=[
            openapi.Parameter('uuid', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the author."),
            openapi.Parameter('post_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the post."),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Page number"),
            openapi.Parameter('size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Number of posts per page"),
        ],
    responses={
        200: CommentListSerializer,
        404: openapi.Response("Author or post not found."),
    }
)
@swagger_auto_schema(
    tags=['comments'],
    method='post',
    operation_description="Creates a comment for the post.",
    request_body=CommentSerializer,
    manual_parameters=[
            openapi.Parameter('uuid', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the author."),
            openapi.Parameter('post_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the post."),
        ],
    responses={
        200: CommentSerializer,
        404: openapi.Response("Author or post not found."),
    }
)
@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_comments(request, uuid, post_id):
    if request.method == 'GET':
        # check if post exists
        post = get_object_or_404(Posts, uuid=post_id, author_uuid=uuid)

        if post.visibility != "PUBLIC":
            return Response(status=404)
        
        comments = Comments.objects.filter(post_id=post_id).order_by('-published')

        page = request.GET.get("page")
        size = request.GET.get("size")

        if not page or not size:
            return Response(status=400, data="Must specify page and size query parameters")

        # if pagination specified, return only the requested range
        if page is not None and size is not None:
            start = (int(page) - 1) * int(size)
            end = start + int(size)
            comments = comments[start:end]

        formatted = []
        for comment in comments:
            data = model_to_dict(comment)
            data["author"] = AuthorDetail(comment.author_uuid, comment.author_url, comment.author_host).formatAuthorInfo()

            for k in ("author_uuid", "author_url", "author_host"):
                data.pop(k)
            
            data["id"] = f"{ENDPOINT}authors/{post.author_uuid}/posts/{post_id}/comments/{data['uuid']}"
            # timestamps get excluded because they're not json serialized
            data["published"] = str(comment.published)

            formatted.append(data)
        
        response_data = {"page": page, 
                         "size": size, 
                         "post": f"{ENDPOINT}authors/{post.author_uuid}/posts/{post_id}",
                         "id": f"{ENDPOINT}authors/{post.author_uuid}/posts/{post_id}/comments",
                         "comments": formatted}
        
        serialized = CommentListSerializer(data=response_data)

        if not serialized.is_valid():
            return Response(status=500, data=serialized.errors)

        return Response(status=200, data=serialized.validated_data)

    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=400, data=serializer.errors)
        
        data = serializer.validated_data
        author_uuid = get_id_from_url(data["author"]["id"])
        author_host = data["author"]["host"]
        author_url = data["author"]["url"]

        comment_url = data["id"]
        comment_uuid = get_part_from_url(comment_url, "comments")

        post_id = get_part_from_url(comment_url, "posts")
        post = get_object_or_404(Posts, uuid=post_id)

        Comments.objects.update_or_create(comment=data["comment"], contentType=data["contentType"], uuid=comment_uuid, post=post, author_uuid=author_uuid, author_host=author_host, author_url=author_url)

        return Response(status=200, data=serializer.validated_data)


# POST LIKES
# =====================
@swagger_auto_schema(
    tags=['likes', 'remote'],
    method='get',
    operation_description="Retrieves the list of likes for a public post.",
    manual_parameters=[
            openapi.Parameter('uuid', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the author."),
            openapi.Parameter('post_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the post."),
        ],
    responses={
        200: LikeListSerializer,
        404: openapi.Response("Post or author not found."),
    }
)
@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_post_likes(request, uuid, post_id):
    author_cache = AuthorCache()

    # TODO auth for private posts
    author = get_object_or_404(AuthorUser, uuid=uuid)
    post = get_object_or_404(Posts, uuid=post_id)

    # TODO check if user should be able to see this post
    if post.visibility != "PUBLIC":
        return Response(status=404)

    likes = Likes.objects.filter(liked_object_type="post", liked_id=post_id).exclude(author_uuid=uuid)
    formatted = []
    for like in likes:
        formatted.append({
            "type": "like",
            "context": like.context,
            "summary": like.summary,
            "author": author_cache.get(like.author_uuid),
            "object": like.liked_object
        })
    
    return Response(status=200, data={"type": "likes", "items": formatted})
        

# COMMENT LIKES
# =====================
@swagger_auto_schema(
    tags=['likes', 'remote'],
    method='get',
    operation_description="Retrieves the list of likes for the provided comment on a public post.",
    manual_parameters=[
            openapi.Parameter('uuid', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the author."),
            openapi.Parameter('post_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the post."),
            openapi.Parameter('comment_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the comment."),
        ],
    responses={
        200: LikeListSerializer,
        404: openapi.Response("Post, comment, or author not found."),
    }
)
@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_comment_likes(request, uuid, post_id, comment_id):
    # TODO auth for private posts
    author_cache = AuthorCache()
    author = get_object_or_404(AuthorUser, uuid=uuid)
    post = get_object_or_404(Posts, uuid=post_id)
    comment = get_object_or_404(Comments, uuid=comment_id)

    likes = Likes.objects.filter(liked_object_type="comment", liked_id=comment_id).exclude(author_uuid=uuid)
    formatted = []
    for like in likes:
        formatted.append({
            "type": "like",
            "context": like.context,
            "summary": like.summary,
            "author": author_cache.get(like.author_uuid),
            "object": like.liked_object
        })
    
    return Response(status=200, data={"type": "likes", "items": formatted})



# LIKED
# =====================
def get_public_likes(uuid):
    nodes = Nodes()
    post_cache = PostCache()

    liked_items = []
    associated_posts = []
    for item in Likes.objects.filter(author_uuid=uuid):
        post_id = get_part_from_url(item.liked_object, "posts")
        try: post = Posts.objects.get(uuid=post_id)
        except Posts.DoesNotExist: post = None

        if post and post.visibility == "PUBLIC":
            associated_posts.append(post)
            liked_items.append(item)

        if not post and post_cache.get(post_id):
            associated_posts.append(post_cache.get(post_id))
            liked_items.append(item)
        
        if not post:
            origin = None
            for host in HOSTS:
                if item.liked_object.startswith(host):
                    origin = host
                    break
            
            if origin:
                try:
                    auth = nodes.get_auth_for_host(origin)
                    headers = {"Accept": "application/json"}

                    if origin == HOSTS[1]:
                        headers["Referer"] = nodes.get_host_for_index(0)

                    response = requests.get(item.liked_object, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)
                    # we can assume that if we get a 2XX response, the post is public
                    if response.ok:
                        post = response.json()
                        associated_posts.append(post)
                        liked_items.append(item)
                except:
                    continue

    return liked_items, associated_posts


@swagger_auto_schema(
    tags=['liked', 'remote'],
    method='get',
    operation_description="Retrieves the public liked items made by the author.",
    manual_parameters=[
            openapi.Parameter('uuid', openapi.IN_PATH, type=openapi.TYPE_STRING, description="The unique identifier for the author."),
        ],
    responses={
        200: LikeListSerializer,
        404: openapi.Response("Author not found."),
    }
)
@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_author_liked(request, uuid):
    author_cache = AuthorCache()
    author = get_object_or_404(AuthorUser, uuid=uuid)

    formatted = []
    items, posts = get_public_likes(uuid)
    for like in items:
        formatted.append({
            "type": "like",
            "context": like.context,
            "summary": like.summary,
            "author": author_cache.get(like.author_uuid),
            "object": like.liked_object
        })
    
    return Response(status=200, data={"type": "likes", "items": items})