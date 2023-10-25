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
        print(picture)

        empty = [element in (None, "") for element in [title, content, visibility]]
        
        if any(empty):
            return super().form_invalid(form)
        else:
            if picture is not None:
                #A picture is included in the post
                pass

            #contentType = self.request.POST.get('contentType')
            author = get_author_info(self.request) # convert author object to dictionary
            count = 0
            # will need to determine content type
            # contentType = "text/plain"
            contentType = "image/png;base64"
            image_base64 = base64.b64encode(picture.read()).decode('utf-8')
            content = image_base64
            comments = ""
            unlisted = False if contentType in ('text/markdown', 'text/plain') else True #make images and other data unlisted so it doesn't show up in a post

            post = Posts(title=title, uuid=unique_id, description=description, contentType=contentType, content=content, categories=categories, visibility=visibility, author=author, count=count, comments=comments, unlisted=unlisted)
            # post.save(force_insert=True)
            
            return redirect('stream')
            # redirect to detail page
            #return HttpResponseRedirect(reverse('posts/detail'), args=(form.instance.author.get("uuid"), post.uuid,))

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
    posts = Posts.objects.all().order_by('-published')
    return render(request, 'posts/dashboard.html', {'all_posts': posts})
