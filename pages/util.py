from accounts.models import AuthorUser
from pages.seralizers import AuthorDetailSerializer, AuthorUserSerializer
from static.vars import ENDPOINT
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

def get_id_from_url(url):
    if url:
        url = url[:-1] if url[-1] == "/" else url
        url = url.split("/")
        return url[-1]
    return ""