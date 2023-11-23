from django.shortcuts import render
import markdown
import commonmark
import yaml
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.

@swagger_auto_schema(methods=['GET'], auto_schema=None)
@api_view(['GET'])
def get_all_connections(request):
    with open('static/remotes.yml') as f:
        connections = yaml.load(f, Loader=yaml.FullLoader)
    return Response(status=200, data=connections)

def docs_viewer(request):
    return render(request, "docs.html")

