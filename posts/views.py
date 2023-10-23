from django.shortcuts import render
from django.views.generic import DetailView, CreateView
from .models import Posts
from .forms import CreatePostForm
from django.http import HttpResponseRedirect
from django.urls import reverse
import uuid

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

        empty = [element in (None, "") for element in [title, content, visibility]]
        
        if any(empty):
            return super().form_invalid(form)
        else:
            #contentType = self.request.POST.get('contentType')
            
            author = {} # TODO grab current user as author
            count = 0
            # will need to determine content type
            contentType = "text/plain"
            comments = ""
            unlisted = False if contentType in ('text/markdown', 'text/plain') else True

            post = Posts(title=title, uuid=unique_id, description=description, contentType=contentType, content=content, categories=categories, visibility=visibility, author=author, count=count, comments=comments, unlisted=unlisted)
            post.save(force_insert=True)
            
            return HttpResponseRedirect("../../posts/all/")
            # redirect to detail page
            #return HttpResponseRedirect(reverse('posts/detail'), args=(form.instance.author.get("uuid"), post.uuid,))

def view_posts(request):
    posts = Posts.objects.all().order_by('-published')
    return render(request, 'posts/detail.html', {'all_posts': posts})

def redir_create(request):
    return HttpResponseRedirect("../../posts/new/")