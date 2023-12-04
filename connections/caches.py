import requests
from cryptography.fernet import Fernet
from django_project import settings
from django_project.settings import FERNET_KEY
from requests.auth import HTTPBasicAuth
from posts.models import Likes, Posts
from static.vars import ENDPOINT, HOSTS
import threading

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
            cls._instance.locks = {}

            # start the thread that updates the cache every 5 minutes
            thread = threading.Timer(300, cls._instance.update)
            thread.daemon = True # program will exit if only daemon threads are left
            thread.start()

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
        """
        Locks are needed here incase the user refreshes the page and the cache is being updated
        simultaneously. I am not sure what happens in this case, but better safe than sorry.
        These locks should cost next to nothing in terms of performance. There should be
        little to no lock contention, and the branch predictor should be able to predict
        the branch correctly almost every time.
        """
        self.initialize()

        # create a lock for this key if it doesn't exist
        if key not in self.locks:
            self.locks[key] = threading.Lock()

        # if the lock is already acquired by another thread, return
        # this cache entry is already being updated, so there is no need to update it again
        if not self.locks[key].acquire(blocking=False):
            return

        # update the value to the cache
        self.cache[key] = value

        # release the lock
        self.locks[key].release()

    def get(self, key):
        self.initialize()
        res = self.cache.get(key)
        if not res:
            try: foreign = ForeignAuthor.objects.get(uuid=key)
            except: foreign = None
            if not foreign:
                print(f"Error getting {key} from cache, updating cache...")
                self.update()
            else:
                return foreign.author_json
        
        # This case should not happen but is a safety
        return self.cache.get(key)
    
    def remove(self, key):
        self.initialize()
        self.cache.pop(key)

        # remove the lock if it exists
        if key in self.locks:
            self.locks.pop(key)

    def clear(self):
        self.cache = {}
        self.locks = {}
    
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

        foreigns = ForeignAuthor.objects.all()
        for f in foreigns:
            self.cache[str(f.uuid)] = f.author_json

        for i in range(len(HOSTS)):
            
            if i == 0:
                authors = AuthorUser.objects.all()
                for auth in authors:
                    obj = {"id": f"{ENDPOINT}authors/{auth.uuid}/",
                    "host": auth.host,
                    "url": auth.url,
                    "github": auth.github,
                    "displayName": auth.username,
                    "profileImage": auth.profile_image}

                    self.cache[auth.uuid] = obj
            
            else:
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

    def incrementLikeCount(self, post_id):
        self.initialize()
        post = self.cache.get(post_id)
        if post:
            post["likeCount"] += 1
            self.cache[post_id] = post

    # TODO grab all local then mess with remotes
    def update(self):
        author_cache = AuthorCache()
        node_singleton = Nodes()

        for post in Posts.objects.all():
            # update likes if diff detected
            likes = Likes.objects.filter(liked_object_type='post', liked_id=post.uuid)
            if len(likes) != post.likeCount:
                post.likeCount = len(likes)
                post.save()
            
            if post.uuid.endswith("_pic"):
                continue

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

                # 404 Not Found
                if strip_slash(details['host']) == HOSTS[1]:
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

                # Web Wizards
                elif strip_slash(details['host']) == HOSTS[2]:
                    try:
                        params = {
                            "page": 1,
                            "size": 20
                        }
                        response = requests.get(posts_url, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers, params=params)
                        if response.ok:
                            posts = response.json()
                            posts = posts["items"]
                            
                            for post in posts:
                                uuid = get_id_from_url(post["id"])
                                try:
                                    url = f"{post['id']}/likes/"
                                    response = requests.get(url, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)

                                    if response.ok:
                                        likes = response.json()
                                        post["likeCount"] = len(likes["items"])
                                except:
                                    post["likeCount"] = 0
                                self.cache[uuid] = post

                    except Exception as e:
                        print(e)
                        continue
                
                # Ctrl-Alt-Dft
                elif strip_slash(details['host']) == HOSTS[3]:
                    try:
                        response = requests.get(posts_url, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)
                        if response.ok:
                            posts = response.json()
                            posts = posts["items"]
                            
                            for post in posts:
                                uuid = get_id_from_url(post["id"])
                                try:
                                    url = f"{post['id']}/likes/"
                                    response = requests.get(url, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)

                                    if response.ok:
                                        likes = response.json()
                                        post["likeCount"] = len(likes["items"])
                                except:
                                    post["likeCount"] = 0
                                self.cache[uuid] = post

                    except Exception as e:
                        print(e)
                        continue
            
                # C404
                elif strip_slash(details['host']) == HOSTS[4]:
                    try:
                        headers = {"Authorization": f"Token {auth[1]}"}
                        response = requests.get(posts_url, headers=headers)

                        if response.ok:
                            posts = response.json()["results"]
                            posts = posts["items"]
                            
                            for post in posts:
                                uuid = get_id_from_url(post["id"])
                                try:
                                    url = f"{post['id']}/likes/"
                                    response = requests.get(url, headers=headers)

                                    if response.ok:
                                        likes = response.json()
                                        post["likeCount"] = len(likes["items"])
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
            if node["host"].startswith(strip_slash(host)):
                return (node["username"], node["password"])
        return None

    def get_api_auth(self):
        self.initialize_values()

        local = self.data[0]
        return (local["username"], local["password"])

