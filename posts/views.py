from django.shortcuts import render, get_object_or_404, redirect 
from django.views.generic import DetailView, CreateView
from django.forms.models import model_to_dict
from .models import Posts
from .forms import CreatePostForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import AuthorUser
import uuid
import base64
from django.http import HttpResponse
from django.http import JsonResponse

class PostCreate(CreateView):
    model = Posts
    template_name = "posts/create.html"
    form_class = CreatePostForm

    def get_success_url(self): # gpt
        return reverse('all')

    def form_valid(self, form):
        # TODO: add author and full link to unique ID, this is merely the hash
        unique_id = uuid.uuid4()

        title = form.cleaned_data.get('title')
        description = form.cleaned_data.get('description')
        content = form.cleaned_data.get('content')
        categories = form.cleaned_data.get('categories')
        visibility = form.cleaned_data.get('visibility')
        picture = form.cleaned_data.get('picture')

        empty = [element in (None, "") for element in [title, content, visibility]]
        
        if any(empty):
            return super().form_invalid(form)
        else:
            contentType = "text/plain"
            author = get_author_info(self.request) # convert author object to dictionary
            count = 0
            comments = ""

            if picture is not None:
                image_base64 = base64.b64encode(picture.read()).decode('utf-8')
                unique_id_pic = str(unique_id) + "_pic"

                #Determine content type:
                if picture.name.endswith(".jpg") or picture.name.endswith(".jpeg"):
                    contentType_pic = "image/jpeg;base64"
                elif picture.name.endswith(".png"):
                    contentType_pic = "image/png;base64"
                else:
                    contentType_pic = "application/base64"

                #save the pic as it's own post
                post_pic = Posts(title=title, uuid=unique_id_pic, description=description, contentType=contentType_pic, content=image_base64, categories=categories, visibility=visibility, author=author, count=count, comments=comments, unlisted=True)
                post_pic.save(force_insert=True)

            post = Posts(title=title, uuid=unique_id, description=description, contentType=contentType, content=content, categories=categories, visibility=visibility, author=author, count=count, comments=comments, unlisted=False)
            post.save(force_insert=True)
            
            return redirect('stream')

def get_author_info(request):
    user = request.user # get db information of current user
    author_obj = get_object_or_404(AuthorUser, username=user) # get db information of author to follow
    full_dict = model_to_dict(author_obj) # convert author object to dictionary
    clean_dict = {"type": "author",
                    "id": full_dict.get("url"),
                    "host": full_dict.get("host"),
                    "displayName": full_dict.get("username"),
                    "url": full_dict.get("url"),
                    "github": full_dict.get("github"),
                    "bio": full_dict.get("bio"),
                    "profileImage": full_dict.get("profile_image")}

    return clean_dict

def view_posts(request):
    posts = Posts.objects.order_by('-published')
    return render(request, 'posts/dashboard.html', {'all_posts': posts})

def like_post_handler(request):
    # Your logic to update data goes here
    updated_data = "New Data"  # Replace with your actual data
    post_uuid = request.GET.get('post_uuid', None)
    author = get_author_info(request) # convert author object to dictionary

    #read post object from db
    try:
        post = Posts.objects.get(uuid=post_uuid)
    except Posts.DoesNotExist:
        print(f"Error: Post with UUID:{post_uuid} does not exist.")
    
    #create and send like object to post creator

    #increment the like count
    post.count = post.count + 1
    post.save()

    print(f"Like button pressed for post {post_uuid} by {author['displayName']}")

    return JsonResponse({'updated_data': updated_data}) #TODO: use this to update the like count
