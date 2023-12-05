from django.shortcuts import render
import markdown
import yaml
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Node
from cryptography.fernet import Fernet
import django_project.settings as settings
from connections.caches import AuthorCache, PostCache
# Create your views here.

@swagger_auto_schema(methods=['GET'], auto_schema=None)
@api_view(['GET'])
def get_all_connections(request):
    with open('static/remotes.yml') as f:
        connections = yaml.load(f, Loader=yaml.FullLoader)
    return Response(status=200, data=connections)

def docs_viewer(request):
    return render(request, "docs.html")

def extra_docs_viewer(request):
    return render(request, "remote_docs.html")

@api_view(['GET'])
def refreshCache(request):
    print("---REFRESH TRIGGERED---")

    t = request.GET.get('type')

    if t == "posts":
        post_cache = PostCache()
        post_cache.update()
    elif t == "authors":
        author_cache = AuthorCache()
        author_cache.update()
    return Response(status=200, data={"message": "Cache updated"})
