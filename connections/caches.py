import requests
from cryptography.fernet import Fernet
from django_project import settings
from django_project.settings import FERNET_KEY
from requests.auth import HTTPBasicAuth
from posts.models import Posts
from static.vars import ENDPOINT, HOSTS

from util import format_local_post, get_id_from_url, strip_slash, format_local_post_from_db
from .models import Node

# CACHE CLASSES
# ====================================================================================================

class Cache():
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = object.__new__(cls)
            cls._instance.init = False
            cls._instance.cache = {}
        return cls._instance
    
    def items(self):
        self.initialize()
        return self.cache.items()
    
    def keys(self):
        self.initialize()
        return self.cache.keys()
    
    def values(self):
        self.initialize()
        return self.cache.values()

    def add(self, key, value):
        self.initialize()
        self.cache[key] = value

    def get(self, key):
        self.initialize()
        return self.cache.get(key)

    def remove(self, key):
        self.initialize()
        self.cache.pop(key)

    def clear(self):
        self.cache = {}
    
    def initialize(self):
        if not self.init:
            self.init = True
            self.update()

    def update(self):
        pass
    

class AuthorCache(Cache):
    def __init__(self):
        super().__init__()
    
    def update(self):
        node_singleton = Nodes()

        for i in range(len(HOSTS)):
            host = HOSTS[i]

            auth = node_singleton.get_auth_for_host(host)
            url = node_singleton.get_host_for_index(i)

            try:
                authors_url = f"{url}/authors/"

                headers={"Accept": "application/json"}
                if i == 1:
                    headers["Referer"] = node_singleton.get_host_for_index(0)
                    
                response = requests.get(authors_url, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)

                if response.ok:
                    authors = response.json()
                    for author in authors["items"]:
                        uuid = get_id_from_url(author["id"])
                        self.cache[uuid] = author
            
            except Exception as e:
                print(e)
                continue

class PostCache(Cache):
    def __init__(self):
        super().__init__()

    # TODO grab all local then mess with remotes
    def update(self):
        author_cache = AuthorCache()
        node_singleton = Nodes()

        for post in Posts.objects.all():
            author_override = author_cache.get(str(post.author_uuid))
            self.cache[post.uuid] = format_local_post(post, author_override)
        
        for author, details in author_cache.items():
            try:
                if details['host'] in (ENDPOINT, f"{node_singleton.get_host_for_index(3)}/"):
                    continue
                    
                elif strip_slash(details['host']) == HOSTS[1]:
                    index = HOSTS.index(strip_slash(details['host']))

                    endpoint = node_singleton.get_host_for_index(index)
                    auth = node_singleton.get_auth_for_host(details["host"])
                    print(endpoint)
                    headers = {"Accept": "application/json", "Referer": node_singleton.get_host_for_index(0)}
                    posts_url = f"{endpoint}/authors/{author}/posts/"
                    print(posts_url)

                    try:
                        response = requests.get(posts_url, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)
                        if response.ok:
                            posts = response.json()
                            
                            for post in posts:
                                uuid = get_id_from_url(post["id"])
                                try:
                                    url = f"{post['id']}/likes/"
                                    response = requests.get(url, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)

                                    if response.ok:
                                        likes = response.json()
                                        post["likeCount"] = len(likes)
                                except:
                                    post["likeCount"] = 0
                                self.cache[uuid] = post

                    except Exception as e:
                        print(e)
                        continue
            except Exception as e:
                print(e)
        
        # print(self.cache)

# NODE DATA SINGLETON - for peer-to-peer requests and connection
# ====================================================================================================

class Nodes():
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = object.__new__(cls)
            cls._instance.init = False
            cls._instance.data = []
        return cls._instance

    def get_host_for_index(self, index):
        try: return Node.objects.get(index=index).host
        except: return None

    def get_values(self):
        self.initialize_values()

        return self.data

    def initialize_values(self):
        if not self.init:
            self.init = True

        cipher_suite = Fernet(settings.FERNET_KEY)
        for node in Node.objects.all():
            try: p_bytes = node.password.tobytes()
            except: p_bytes = node.password
            self.data.append({
                "host": node.host,
                "username": node.username,
                "password": cipher_suite.decrypt(p_bytes).decode()
            })
    
    def get_auth_for_host(self, host):
        self.initialize_values()
        
        for node in self.data:
            if node["host"].startswith(host):
                return (node["username"], node["password"])
        return None

    def get_api_auth(self):
        self.initialize_values()

        local = self.data[0]
        return (local["username"], local["password"])

