from django.shortcuts import render
from inbox.serializers import InboxSerializer, InboxItemSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from accounts.models import AuthorUser
from .models import Inbox
from drf_yasg.utils import swagger_auto_schema
from .serializers import InboxSerializer, InboxItemSerializer

# Create your views here.
@swagger_auto_schema(
    methods=['GET'],
    operation_description="Test",
)
@swagger_auto_schema(
    methods=['POST'],
    operation_description="Test the sequel",
    request_body=InboxItemSerializer,
)
@api_view(['GET', 'POST', 'DELETE'])
def api_inbox(request, pk):
    
    author = get_object_or_404(AuthorUser, pk=pk)

    if request.user.id != author.id:
        return Response(status=404)
    
    try:
        inbox = Inbox.objects.get(author=author.uuid)
    except Inbox.DoesNotExist:
        inbox = Inbox.objects.create(author=author, items=[])

    if request.method == 'GET':
        if not request.user.is_authenticated:
            return Response(status=401, data="You must be logged in to follow someone")
        
        # get a list of posts sent to author_id (paginated)
        posts = []

        for item in inbox.items:
            if item["type"] == "post":
                posts.append(item)

        # check query params for pagination
        page = request.GET.get("page")
        size = request.GET.get("size")
    
        # # if pagination specified, return only the requested range
        if page is not None and size is not None:
            start = (int(page) - 1) * int(size)
            end = start + int(size)
            posts = posts[start:end]

        inbox.items = posts

        serializer = InboxSerializer(inbox)
        return Response(serializer.data)

    elif request.method == 'POST':
        
        serializer = InboxItemSerializer(data=request.data, partial=False)

        if not serializer.is_valid():
            return Response(status=400, data=serializer.errors)
        
        new_item = serializer.validated_data
        inbox.items.append(new_item)
        inbox.save()

        # respond with 200 and the inbox item json
        return Response(status=200, data=serializer.validated_data)

    elif request.method == 'DELETE':
        inbox.items.clear()
        inbox.save()
        return Response(status=204)