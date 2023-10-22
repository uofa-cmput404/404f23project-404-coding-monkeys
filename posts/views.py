from django.shortcuts import render
from django.views.generic import DetailView
from .models import Posts
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

def upload(request):
    print(request)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        contentType = request.POST.get('contentType')
        content = request.POST.get('content')
        categories = request.POST.get('categories')
        visibility = request.POST.get('visibility')

        empty = [element in (None, "") for element in [title, description, contentType, content, categories, visibility]]
        
        if any(empty):
            return render(request, 'posts/create.html', {'error': 'Please fill in all the fields'})
        else:
            author = {} # TODO grab current user as author
            count = 0
            comments = ""
            published = datetime.datetime.now().isoformat()
            unlisted = False if contentType in ('text/markdown', 'text/plain') else True

            post = Posts(title=title, description=description, contentType=contentType, content=content, categories=categories, visibility=visibility, author=author, count=count, comments=comments, published=published, unlisted=unlisted)
            post.save()
            # redirect to detail page
            return HttpResponseRedirect(reverse('polls:detail'), args=(author.get("uuid"), post.uuid,))

class PostDetail(DetailView):
    model = Posts
    fields = ['title', 'description', 'contentType', 'content', 'categories', 'visibility', 'author', 'count', 'comments', 'published']
    template_name = 'posts/detail.html'
