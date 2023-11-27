import requests
from cryptography.fernet import Fernet
from django_project import settings
from django_project.settings import FERNET_KEY
from requests.auth import HTTPBasicAuth
from static.vars import ENDPOINT, HOSTS

from util import get_id_from_url
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

        for host in HOSTS:
            auth = node_singleton.get_auth_for_host(host)
        
            try:
                authors_url = f"{host}/authors/"
                response = requests.get(authors_url, auth=HTTPBasicAuth(auth[0], auth[1]))

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

        for author, details in author_cache.items():
            try:
                if details['host'] == ENDPOINT:
                    
                    posts_url = f"{details['host']}authors/{author}/posts?page=1&size=100"
                    host = details['host'] if details['host'][-1] != "/" else details['host'][:-1]

                # auth = get_auth_for_host(host)
                
                response = requests.get(posts_url)
                if response.ok:
                    posts = response.json()
                    
                    for post in posts["items"]:
                        uuid = get_id_from_url(post["id"])
                        self.cache[uuid] = post
            except Exception as e:
                print(e)
                continue

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

    def get_values(self):
        self.initialize_values()

        return self.data

    def initialize_values(self):
        if not self.init:
            self.init = True

        cipher_suite = Fernet(settings.FERNET_KEY)
        for node in Node.objects.all():
            print(type(node.password))
            self.data.append({
                "host": node.host,
                "username": node.username,
                "password": cipher_suite.decrypt(node.password).decode()
            })
    
    def get_auth_for_host(self, host):
        self.initialize_values()

        for node in self.data:
            if node["host"] == host:
                return (node["username"], node["password"])
        return None

    def get_api_auth(self):
        self.initialize_values()

        local = self.data[0]
        return (local["username"], local["password"])

