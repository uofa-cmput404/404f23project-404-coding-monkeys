# this represents static variables that are used throughout various parts of the application
from django.test import Client

# this is the DEV URL of our webserver; we'll need a PROD URL later when we actually deploy
ENDPOINT = "http://www.chimp-chat.win/"
NODES = []
HOSTS = ["http://www.chimp-chat.win"]
CLIENT = Client()

class Cache():
    def __init__(self):
        self.cache = {}

    def items(self):
        return self.cache.items()
    
    def keys(self):
        return self.cache.keys()
    
    def values(self):
        return self.cache.values()

    def add(self, key, value):
        self.cache[key] = value

    def get(self, key):
        return self.cache.get(key)

    def remove(self, key):
        self.cache.pop(key)

    def clear(self):
        self.cache = {}

AUTHOR_CACHE = Cache()
POST_CACHE = Cache()
