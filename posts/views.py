import json
from django.shortcuts import render, get_object_or_404, redirect 
from django.views.generic import CreateView
from django.forms.models import model_to_dict
from pages.seralizers import AuthorUserSerializer
from pages.util import AuthorDetail
from pages.views import get_id_from_url
from rest_framework.response import Response
from posts.serializers import LocalCommentSerializer, LocalPostsSerializer, PostsSerializer, ResponsePosts
from .models import Posts, Likes, Comments
from .forms import PostForm
from django.urls import reverse
from accounts.models import AuthorUser, Followers
import uuid
import base64
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.core.files.base import ContentFile
from PIL import Image
from drf_yasg.utils import swagger_auto_schema
from static.vars import ENDPOINT
from django.http import HttpResponse
from django.core.serializers import serialize
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import copy


class PostCreate(CreateView):
    model = Posts
    template_name = "posts/create.html"
    form_class = PostForm

    def get_success_url(self): # gpt
        return reverse('all')

def make_new_post(request, form=None):
    if request.method == 'GET':
        try:
            authors = AuthorUser.objects.exclude(id=request.user.id)
        except AuthorUser.DoesNotExist:
            authors = []
        
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
        post = Posts(uuid=unique_id, author=author, contentType="text/plain", count=0, comments="", unlisted=False)

    unique_id_pic = str(unique_id) + "_pic"

    post.title = request.POST.get('title')
    post.description = request.POST.get('description')
    post.content = request.POST.get('content')
    post.categories = request.POST.get('categories')
    post.comments = f"http://127.0.0.1:8000/authors/{post.author['id']}/posts/{post.uuid}/comments"
    post.visibility = request.POST.get('visibility')

    if request.POST.get('author_list') and post.visibility == "PRIVATE":
        selected_author_id = request.POST.get('author_list')
        post.sharedWith = get_author_info(selected_author_id)

    post.save()
    
    # deal with updating picture
    try:
        post = Posts.objects.get(uuid=unique_id_pic)
    except Posts.DoesNotExist:
        post.uuid = unique_id_pic
        post.unlisted = True

    # update existing pic post
    if request.FILES.get('picture') is not None:
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

def delete_post(request, author_id, post_uuid):
    if request.method == 'GET':
        #read the post (whose like button the user clicked) object from db
        try:
            post = Posts.objects.get(uuid=post_uuid)
            post.delete()

            pic_post = Posts.objects.get(uuid=f'{post_uuid}_pic')
            pic_post.delete()
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


def determine_if_friends(current_followers : list, user_id : str, post_author_id : str):
    try:
        row = Followers.objects.get(author_id=post_author_id)
        author_followers = [follower['id'] for follower in row.followers]
    except Followers.DoesNotExist:
        author_followers = []
    
    return post_author_id in current_followers and user_id in author_followers


def view_posts(request):
    author_id = request.user.id
    viewable = []
    determined_friends = set()
    # exclude picture posts since they're dealt with in the html template
    posts = Posts.objects.order_by('-published')

    try:
        row = Followers.objects.get(author_id=author_id)
        current_followers = [follower['id'] for follower in row.followers]
    except Followers.DoesNotExist:
        current_followers = []

    for post in posts:
        if post.visibility == "PUBLIC":
            viewable.append(post)

        # show own posts
        elif post.author['id'] == author_id:
            viewable.append(post)

        elif post.visibility == "FRIENDS":
            if post.author['id'] in determined_friends or determine_if_friends(current_followers, author_id, post.author['id']):
                viewable.append(post)
                determined_friends.add(post.author['id'])

        elif post.visibility == "PRIVATE":
            sharedWith = post.sharedWith.get('id', None)
            if sharedWith == author_id:
                viewable.append(post)

    return render(request, 'posts/dashboard.html', {'all_posts': viewable})

def format_comment(comment):
    comment_obj = model_to_dict(comment)
    ad = AuthorDetail(comment.author_uuid, comment.author_url, comment.author_host)

    for k in ("author_uuid", "author_url", "author_host"):
        comment_obj.pop(k)

    comment_obj["author"] = ad.formatAuthorInfo()
    # idk why these were excluded
    comment_obj["published"] = str(comment.published)
    comment_obj["post_id"] = str(comment.post_id)

    return comment_obj

def open_comments_handler(request):
    # returns commenets for a given post
    post_uuid = request.GET.get('post_uuid')
    comments = Comments.objects.filter(post_id=post_uuid)

    formatted = []
    for comment in comments:
        formatted.append(format_comment(comment))
    
    serialized = LocalCommentSerializer(data=formatted, many=True)
    
    if not serialized.is_valid():
        return JsonResponse({'comments': '{}'})
    #TODO: sort newest to oldest?
    return JsonResponse({'comments': json.dumps(serialized.validated_data)})


def submit_comment_handler(request):
    post_uuid = request.GET.get('post_uuid', None) #get the post in question
    commentText = request.GET.get('comment_text', None) #get the text of the comment
    author = AuthorUser.objects.get(id=request.user.id) #get the current user

    #read the post (whose like button the user clicked) object from db
    try: post = Posts.objects.get(uuid=post_uuid)
    except Posts.DoesNotExist: print(f"Error: Post with UUID:{post_uuid} does not exist.")

    post.count += 1
    post.save()
    

    print(f"{author.username} entered comment handler for post: {post_uuid}")
    print(f"Comment contents: {commentText}")


    #create and save new comment object
    commentID = ""
    # Example ID
    # "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
    #       http://127.0.0.1:8000/authors/[ID OF POST AUTHOR]                     /posts/[ID OF POST]              /comments/[ID OF COMMENT]
    # commentID = f"http://127.0.0.1:8000/authors/{post.author['id']}/posts/{post.uuid}/comments/{uuid.uuid4()}"
    commentID = uuid.uuid4()
    commentPost = post
    commentText = commentText

    authorID = author.uuid
    authorHost = author.host
    authorURL = author.url

    commentObj = Comments(uuid= commentID, post= commentPost, comment= commentText, author_uuid=authorID, author_host=authorHost, author_url=authorURL, contentType= "text/plain")
    commentObj.save(force_insert=True)

    newComment = Comments.objects.get(uuid=commentID)
    formattedComment = format_comment(newComment)
    return JsonResponse({'comments': json.dumps([formattedComment])})

def get_object_type(url):
    sections = url.split("/")
    return "post" if sections[-2] == "posts" else "comment"

def like_post_handler(request):
    #The user has clicked the like button for a post.

    post_uuid = request.GET.get('post_uuid', None) #get the post in question
    author = AuthorUser.objects.get(uuid=request.user.uuid) #get the current user

    #read the post (whose like button the user clicked) object from db
    try: post = Posts.objects.get(uuid=post_uuid)
    except Posts.DoesNotExist: print(f"Error: Post with UUID:{post_uuid} does not exist.")

    #get list of all of the current user's likes
    likes = Likes.objects.filter(author_uuid=request.user.uuid)

    #find out if user has already liked this post
    alreadyLikedPost = False
    existingLikeObj = None
    for like in likes:
        if like.liked_object.endswith(post.uuid):
            alreadyLikedPost = True
            existingLikeObj = like
            break

    if alreadyLikedPost:
        existingLikeObj.delete()#remove like from db

        #decrement like counter
        post.likeCount = post.likeCount - 1
        post.save()
    
    else:
        #create and save new like object
        likeContext = "TODO: IDK what to put here"
        likeSummary = f"{author.username} likes your post"

        likeAuthorID = author.uuid
        likeAuthorHost = author.host
        likeAuthorURL = author.url

        postObjLnk = f"http://127.0.0.1:8000/authors/{post.author_uuid}/posts/{post.uuid}"
        likedObjType = "post"
        likeObj = Likes(context= likeContext, summary= likeSummary, author_uuid=author.uuid, author_host=author.host, author_url=author.url, liked_object_type=likedObjType, liked_object= postObjLnk)
        likeObj.save(force_insert=True)

        #increment the like count
        post.likeCount = post.likeCount + 1
        post.save()
        print(f"User: {author.username} has liked post:{post_uuid}")
    


    return JsonResponse({'new_post_count': post.likeCount}) #return new post count

def format_local_post(post):
    post_data = model_to_dict(post)
    post_data["type"] = "post"
    
    ad = AuthorDetail(post.author_uuid, post.author_url, post.author_host)
    post_data["author"] = ad.formatAuthorInfo()

    for key in ("author_uuid", "author_local", "author_url", "author_host"):
        post_data.pop(key)
    
    return post_data

@swagger_auto_schema(
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
    methods=['post', 'delete', 'put'],
    auto_schema=None,
    request_body=PostsSerializer
)
@api_view(['GET', 'POST', 'DELETE', 'PUT'])
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
        
        serializer = LocalPostsSerializer(post, data=post_data, partial=True)
        
        if not serializer.is_valid():
            return Response(status=500, data=serializer.errors)

        return Response(serializer.validated_data)

    # print(request.user.uuid)
    # print(uuid)
    # if request.user.uuid != uuid:
    #     return Response(status=403, data="You are not authorized to edit this post")
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response(status=401, data="You must be logged in to edit a post")
        
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

def test(request):
    return render(request, 'posts/test.html')

@swagger_auto_schema(
    method='get',
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
        

@swagger_auto_schema(
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
    method='post',
    auto_schema=None,
)
@api_view(['GET', 'POST'])
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
            formatted.append(format_local_post(post))

        serializer = LocalPostsSerializer(posts, data=formatted, many=True, partial=True)

        if not serializer.is_valid():
            return Response(status=500, data=serializer.errors)
        
        response = {"type": "posts", "items": serializer.validated_data}
        return Response(response)
    elif request.method == 'POST':
        pass