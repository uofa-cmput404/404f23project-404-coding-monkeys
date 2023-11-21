from django.shortcuts import render
from inbox.serializers import InboxSerializer, InboxItemSerializer
from pages.seralizers import AuthorUserSerializerDB, CommentSerializer, FollowRequestsSerializer, LikeSerializer
from pages.util import AuthorDetail
from posts.models import Comments, Likes, Posts
from posts.serializers import PostsSerializer
from posts.views import get_object_type
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from accounts.models import AuthorUser, FollowRequests
from static.vars import ENDPOINT
from .models import Inbox
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import InboxSerializer, InboxItemSerializer
from pages.views import get_id_from_url, get_part_from_url

class InboxItem():
    def __init__(self, itemType, itemID):
        self.itemType = itemType
        self.itemID = itemID
    def formMapping(self):
        return {
            "type": self.itemType,
            "id": self.itemID
        }
    def checkSame(self, saved):
        if self.itemType == saved.get("type") and self.itemID == saved.get("id"):
            return True
        return False

# Create your views here.
@swagger_auto_schema(methods=['GET'], auto_schema=None, operation_description="Test",)
@swagger_auto_schema(methods=['POST'], operation_description="Test the sequel", request_body=InboxItemSerializer)
@swagger_auto_schema(methods=['DELETE'], auto_schema=None, operation_description="Test",)
@api_view(['GET', 'POST', 'DELETE'])
def api_inbox(request, uuid):
    
    author = get_object_or_404(AuthorUser, uuid=uuid)

    try:
        inbox = Inbox.objects.get(author=author.uuid)
    except Inbox.DoesNotExist:
        inbox = Inbox.objects.create(author=author, items=[])

    if request.method == 'GET':
        if request.user.id != author.id:
            return Response(status=404)
        
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
        
        # check if author even exists
        get_object_or_404(AuthorUser, uuid=uuid)

        try:
            print(request.META.get('REMOTE_ADDR'))
            print(request.user.id)
            print(request.user.uuid)
        except:
            pass

        object_type = request.data.get("type", "").lower()
        if object_type not in ("post", "follow", "like", "comment"):
            return Response(status=400, data="Invalid request. Type must be one of {'post', 'follow', 'like', 'comment'}")
        
        itemType = object_type
        itemID = None

        if object_type == "post":
            
            serializer = PostsSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=400, data=serializer.errors)
            
            data = serializer.validated_data

            post_data = dict(data)
            author = post_data.pop("author")
            post_data["author_uuid"] = get_id_from_url(author.get("id"))
            post_data["author_local"] = author.get("host") == ENDPOINT
            post_data["author_url"] = author.get("url")
            post_data["author_host"] = author.get("host")

            post_data["uuid"] = get_part_from_url(post_data["id"], "posts")

            for extra in ("type","id"):
                post_data.pop(extra)

            try: post = Posts.objects.get(uuid=post_data["uuid"])
            except Posts.DoesNotExist: post = None

            # update visibility
            if post and data["visibility"] != "PUBLIC":
                # shared with current author
                shared_author = AuthorUser.objects.get(uuid=uuid)
                ad = AuthorDetail(shared_author.uuid, shared_author.url, shared_author.host)
                author_obj = ad.formMapping()
                if author_obj not in post.sharedWith:
                    post.sharedWith.append(author_obj)
                    post.save()
            
            itemID = post_data["uuid"]

            if post:
                post_data.pop("uuid")
                Posts.objects.update(**post_data)
            else:
                Posts.objects.update_or_create(**post_data)
            
        
        elif object_type == "follow":
            serializer = FollowRequestsSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=400, data=serializer.errors)
            
            data = serializer.validated_data
            summary = data["summary"]
            requester_uuid = get_id_from_url(data["actor"]["id"])
            requester_host = data["actor"]["host"]
            requester_url = data["actor"]["url"]

            FollowRequests.objects.update_or_create(summary=summary, recipient_uuid=uuid, requester_uuid=requester_uuid, requester_host=requester_host, requester_url=requester_url)

            frq = FollowRequests.objects.get(recipient_uuid=uuid, requester_uuid=requester_uuid)
            itemID = frq.id
        
        elif object_type == "like":
            serializer = LikeSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=400, data=serializer.errors)
            
            data = serializer.validated_data
            author_uuid = get_id_from_url(data["author"]["id"])
            author_host = data["author"]["host"]
            author_url = data["author"]["url"]

            obj_type = get_object_type(data["object"])

            Likes.objects.update_or_create(context = data["context"], summary = data["summary"], author_uuid=author_uuid, author_host=author_host, author_url=author_url, liked_object_type=obj_type, liked_object=data["object"])

            like = Likes.objects.get(author_uuid=author_uuid, liked_object=data["object"])
            itemID = like.id

        elif object_type == "comment":
            serializer = CommentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=400, data=serializer.errors)
            
            data = serializer.validated_data
            author_uuid = get_id_from_url(data["author"]["id"])
            author_host = data["author"]["host"]
            author_url = data["author"]["url"]

            comment_url = data["id"]
            comment_uuid = get_part_from_url(comment_url, "comments")

            post_id = get_part_from_url(comment_url, "posts")
            post = get_object_or_404(Posts, uuid=post_id)

            Comments.objects.update_or_create(comment=data["comment"], contentType=data["contentType"], uuid=comment_uuid, post=post, author_uuid=author_uuid, author_host=author_host, author_url=author_url)

            itemID = comment_uuid

        
        item = InboxItem(itemType, itemID)
        found = -1
        for i in range(len(inbox.items)):
            if item.checkSame(inbox.items[i]):
                found = i
        
        if found != -1:
            del inbox.items[found]
        
        inbox.items.append(item.formMapping())
        inbox.save()

        # respond with 200 and the inbox item json
        return Response(status=200, data=serializer.validated_data)

    elif request.method == 'DELETE':
        if request.user.id != author.id:
            return Response(status=404)
    
        inbox.items.clear()
        inbox.save()
        return Response(status=204)