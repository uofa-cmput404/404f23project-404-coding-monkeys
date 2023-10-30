from django.shortcuts import render, get_object_or_404, redirect 
from django.views.generic import CreateView
from django.forms.models import model_to_dict
from .models import Posts, Likes
from .forms import PostForm
from django.urls import reverse
from accounts.models import AuthorUser, Followers
import uuid
import base64
from django.http import JsonResponse
from django.core.files.base import ContentFile
from PIL import Image

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
                    "id": full_dict.get("id"),
                    "host": full_dict.get("host"),
                    "displayName": full_dict.get("username"),
                    "url": full_dict.get("url"),
                    "github": full_dict.get("github"),
                    "bio": full_dict.get("bio"),
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

def like_post_handler(request):
    #The user has clicked the like button for a post.

    post_uuid = request.GET.get('post_uuid', None) #get the post in question
    author = get_author_info(request.user.id) #get the current user

    #read the post (whose like button the user clicked) object from db
    try: post = Posts.objects.get(uuid=post_uuid)
    except Posts.DoesNotExist: print(f"Error: Post with UUID:{post_uuid} does not exist.")

    #get list of all of the current user's likes
    likes = Likes.objects.filter(author=author)

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
        post.count = post.count - 1 #TODO: post.count is supposed to be the total number of comments, not likes
        post.save()
    
    else:
        #create and save new like object
        likeContext = "TODO: IDK what to put here"
        likeSummary = f"{author['displayName']} likes your post"
        likeAuthor = author
        likeVisibility = "TODO: Idk what to put here"
        postObjLnk = f"http://127.0.0.1:8000/authors/{post.author['id']}/posts/{post.uuid}" #TODO: For some reason the post.author["id"] is an empty string instead of a proper id
        likeObj = Likes(context= likeContext, summary= likeSummary, author=likeAuthor, liked_object= postObjLnk)
        likeObj.save(force_insert=True)

        #increment the like count
        post.count = post.count + 1
        post.save()
        print(f"User: {author['displayName']} has liked post:{post_uuid}")
    


    return JsonResponse({'new_post_count': post.count}) #return new post count
