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
from static.vars import NODES, CLIENT
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

def get_auth_for_host(host):
    global NODES 

    if len(NODES) == 0:
        NODES = get_nodes_info()
        print(NODES)
    
    for node in NODES:
        if node["host"] == host:
            return (node["username"], node["password"])
    return None

def get_api_auth():
    global NODES 

    if len(NODES) == 0:
        NODES = get_nodes_info()
    
    local = NODES[0]
    return (local["username"], local["password"])

def get_nodes_info():
    global CLIENT

    nodes = []
    cipher_suite = Fernet(settings.FERNET_KEY)
    for node in Node.objects.all():
        nodes.append({
            "host": node.host,
            "username": node.username,
            "password": cipher_suite.decrypt(node.password).decode()
        })
    
    return nodes