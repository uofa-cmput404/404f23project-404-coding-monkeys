from django.shortcuts import render
import yaml
from rest_framework.response import Response
from rest_framework.decorators import api_view
# Create your views here.

@api_view(['GET'])
def get_all_connections(request):
    with open('static/remotes.yml') as f:
        connections = yaml.load(f, Loader=yaml.FullLoader)
    return Response(status=200, data=connections)