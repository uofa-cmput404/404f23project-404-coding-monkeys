import datetime
from django.forms import model_to_dict
import pytz
from posts.models import Posts
from static.vars import ENDPOINT
from accounts.models import AuthorUser
from pages.seralizers import AuthorDetailSerializer, AuthorUserSerializer
import requests


class AuthorDetail():

    def __init__(self, uuid="", url="", host=""):
        self.uuid = uuid
        self.url = url
        self.host = host
        self.isLocal = self.host == ENDPOINT
    
    def setMapping(self, detail_mapping):
        self.uuid = detail_mapping.get("uuid")
        self.url = detail_mapping.get("url")
        self.host = detail_mapping.get("host")
        self.isLocal = self.host == ENDPOINT

    def formMapping(self):
        return {
            "uuid": self.uuid,
            "url": self.url,
            "host": self.host,
            "isLocal": self.isLocal
        }

    def setMappingFromAPI(self, api_author_dict):
        self.uuid = get_id_from_url(api_author_dict.get("id"))
        self.url = api_author_dict.get("url")
        self.host = api_author_dict.get("host")
        self.isLocal = self.url == ENDPOINT

    def formatAuthorInfo(self):
        default = {"id": self.host,
                "host": self.host,
                "url": self.url,
                "github": None,
                "displayName": "User Not Found",
                "profileImage": f"{ENDPOINT}static/images/monkey_icon.jpg"}
        
        if self.isLocal:
            author = AuthorUser.objects.get(uuid=self.uuid)
            serializer = AuthorUserSerializer(author)
            return serializer.data
            
        try:
            request = self.url
            response = requests.get(request)
            if response.ok:
                author = response.json()
                serializer = AuthorDetailSerializer(data=author, timeout=1)
                if serializer.is_valid():
                    return serializer.validated_data
        except:
            return default
    
        return default

strip_slash = lambda url: url[:-1] if url[-1] == "/" else url

def get_id_from_url(url):
    if url:
        url = url[:-1] if url[-1] == "/" else url
        url = url.split("/")
        return url[-1]
    return ""

def get_part_from_url(url, part):
    # part is one of authors, posts, or comments and will return the id for that part
    if url:
        url = url[:-1] if url[-1] == "/" else url
        url = url.split("/")

        index = 0
        while index < len(url) and url[index] != part:
            index += 1
        
        # return id right after we find the part
        return url[index+1] if index < len(url) - 1 else ""
    return ""

def time_since_posted(created_at):
    import humanize
    # Parse the created_at timestamp string into a datetime object
    timezone = pytz.timezone("America/Edmonton")
    try: created_at_datetime = datetime.datetime.fromisoformat(created_at)
    except: created_at_datetime = datetime.datetime.fromisoformat(created_at[:-1]).replace(tzinfo=timezone)
    # Get the current time
    current_time = datetime.datetime.now(tz=timezone)

    # Calculate the time difference
    time_difference = current_time - created_at_datetime

    # Use humanize to get a human-readable representation
    return humanize.naturaltime(time_difference)

def format_local_post_from_db(post: Posts):
    post_data = model_to_dict(post)

    ad = AuthorDetail(post.author_uuid, post.author_url, post.author_host)
    author = ad.formatAuthorInfo()

    post_data.update({
        "author": author,
        "type": "post",
        "id": f"{ENDPOINT}authors/{post.author_uuid}/posts/{post.uuid}",
        "published": str(post.published),
        "author_uuid": post.author_uuid,
        "uuid": post.uuid,
        "delta": time_since_posted(str(post.published))
    })

    for k in ("author_url", "author_local", "author_host", "sharedWith"):
        post_data.pop(k)

    return post_data

def format_local_post(post, author_details=None):
    post_data = model_to_dict(post)
    post_data["type"] = "post"
    post_data["id"] = f"{ENDPOINT}authors/{post.author_uuid}/posts/{post.uuid}"
    post_data["published"] = str(post.published)

    if not author_details:
        ad = AuthorDetail(post.author_uuid, post.author_url, post.author_host)
        post_data["author"] = ad.formatAuthorInfo()
    else:
        post_data["author"] = author_details

    for key in ("author_uuid", "author_local", "author_url", "author_host"):
        post_data.pop(key)
    
    return post_data

