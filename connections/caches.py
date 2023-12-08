import requests
from cryptography.fernet import Fernet
from accounts.models import AuthorUser, ForeignAuthor
from django_project import settings
from django_project.settings import FERNET_KEY
from requests.auth import HTTPBasicAuth
from posts.models import Comments, Likes, Posts
from static.vars import ENDPOINT, HOSTS
import threading
import bleach

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
            self.update()
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
    
    def get(self, key):
        self.initialize()
        res = self.cache.get(key)
        if not res:
            self.update()
            try: foreign = ForeignAuthor.objects.get(uuid=key)
            except: foreign = None

            if self.cache.get(key):
                return self.cache.get(key)
            elif not foreign:
                obj = {"displayName":"An Unknown Remote Author", "profileImage": 'https://t3.ftcdn.net/jpg/05/71/08/24/360_F_571082432_Qq45LQGlZsuby0ZGbrd79aUTSQikgcgc.jpg'}
                fa = ForeignAuthor(uuid=key, author_json=obj)
                self.cache[key] = obj
                fa.save()
            else:
                return foreign.author_json
        
        # This case should not happen but is a safety
        return self.cache.get(key)

    def update(self):
        node_singleton = Nodes()

        foreigns = ForeignAuthor.objects.all()
        for f in foreigns:
            self.cache[str(f.uuid)] = f.author_json

        authors = AuthorUser.objects.all()
        for a in authors:
            url = f"{strip_slash(ENDPOINT)}/authors/{a.uuid}"

            if not a.profile_image:
                a.profile_image = 'https://t3.ftcdn.net/jpg/05/71/08/24/360_F_571082432_Qq45LQGlZsuby0ZGbrd79aUTSQikgcgc.jpg'

            author_json = {"id": url,
                           "type": "author",
                           "displayName": a.username,
                           "github": a.github,
                           "profileImage": a.profile_image,
                           "url": url,
                           "host": a.host}
            
            self.cache[str(a.uuid)] = author_json

        for i in range(1, len(HOSTS)):
            host = HOSTS[i]

            auth = node_singleton.get_auth_for_host(host)
            url = node_singleton.get_host_for_index(i)
            try:
                authors_url = f"{url}/authors/"
                print(authors_url)

                headers={"Accept": "application/json"}
                if i < 4:
                    headers["Referer"] = node_singleton.get_host_for_index(0)
                    response = requests.get(authors_url, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)

                    if response.ok:
                        authors = response.json()

                        for author in authors["items"]:
                            uuid = get_id_from_url(author["id"])
                            
                            if author["profileImage"] in (None, ""):
                                author["profileImage"] = 'https://t3.ftcdn.net/jpg/05/71/08/24/360_F_571082432_Qq45LQGlZsuby0ZGbrd79aUTSQikgcgc.jpg'

                            self.cache[uuid] = author
                else:
                    headers["Authorization"] = f"Token: {auth[1]}"
                    response = requests.get(authors_url, headers=headers)

                    if response.ok:
                        authors = response.json()["results"]

                        for author in authors["items"]:
                            uuid = author["id"]
                            author["profileImage"] = author.pop("profilePicture")

                            for k in ("is_active", "created", "updated", "followed", "following"):
                                try: author.pop(k)
                                except: continue
                            
                            if author["profileImage"] in (None, ""):
                                author["profileImage"] = 'https://t3.ftcdn.net/jpg/05/71/08/24/360_F_571082432_Qq45LQGlZsuby0ZGbrd79aUTSQikgcgc.jpg'
                            
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
        if post and not post.get("likeCount"):
            self.cache[post_id]["likeCount"] = 1
        elif post:
            post["likeCount"] += 1
            self.cache[post_id] = post

    def update(self):
        self.pull_posts_local()
        self.grab_all_posts()

    def pull_posts_local(self):
        author_cache = AuthorCache()

        for post in Posts.objects.all():

            likes = Likes.objects.filter(liked_object_type='post', liked_id=post.uuid)
            post.likeCount = len(likes)

            comments = Comments.objects.filter(post=post)
            post.count = len(comments)
            post.save()
            
            author_override = author_cache.get(str(post.author_uuid))

            if post.uuid.endswith("_pic"):
                try: 
                    parent_post = Posts.objects.get(uuid=post.uuid[:-4])
                    post_dict = format_local_post(parent_post, author_override)
                    post_dict["image"] = f"{strip_slash(parent_post.origin)}/image/"

                    content_embedded_img = parent_post.content
                    split = content_embedded_img.split("\n")
                    pure_content = split[:-1]
                    post_dict["content"] = "\n".join(pure_content)

                    post = parent_post

                except Exception as e:
                    print(e)
                    continue
            else:
                post_dict = format_local_post(post, author_override)
            
            self.cache[post.uuid] = post_dict

    def sort_posts(self):
        author_cache = AuthorCache()
        node_singleton = Nodes()

        node_post_list = [[],[],[],[],[]]

        for author, details in author_cache.items():
            try:
                index = HOSTS.index(strip_slash(details['host']))
                node_post_list[index].append((author, details))
            except:
                continue
        
        return node_post_list

    def grab_all_posts(self):
        master_list = self.sort_posts()
        for i in range(len(master_list)):
            node_authors = master_list[i]
            thread = threading.Thread(target=self.pull_authors, args=(node_authors, i))
            thread.start()

    # TODO grab all local then mess with remotes
    def pull_authors(self, node_authors, node_index):
        node_singleton = Nodes()
        for author, details in node_authors:
            try:
                # skip local posts
                if node_index == 0 or strip_slash(details.get('host')) != HOSTS[node_index]:
                    continue
                
                index = HOSTS.index(strip_slash(details['host']))
                endpoint = node_singleton.get_host_for_index(index)
                auth = node_singleton.get_auth_for_host(details["host"])
                headers = {"Accept": "application/json"}
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
                                    else:
                                        post["likeCount"] = 0
                                except:
                                    post["likeCount"] = 0

                                try:
                                    url = f"{strip_slash(post['origin'])}/image/"
                                    response = requests.get(url, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)

                                    if response.ok:
                                        post["image"] = url
                                except Exception as e:
                                    print(e)

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
                                    else:
                                        post["likeCount"] = 0
                                except:
                                    post["likeCount"] = 0
                                
                                try:
                                    url = f"{strip_slash(post['origin'])}/image/"
                                    response = requests.get(url, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)

                                    if response.ok:
                                        post["image"] = url
                                except Exception as e:
                                    print(e)

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
                                    else:
                                        post["likeCount"] = 0
                                except:
                                    post["likeCount"] = 0

                                try:
                                    url = f"{strip_slash(post['origin'])}/image/"
                                    response = requests.get(url, auth=HTTPBasicAuth(auth[0], auth[1]), headers=headers)

                                    if response.ok:
                                        post["image"] = url
                                except Exception as e:
                                    print(e)
                                
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
                                    else:
                                        post["likeCount"] = 0
                                except:
                                    post["likeCount"] = 0
                                
                                self.cache[uuid] = post

                    except Exception as e:
                        print(e)
                        continue
            
            except Exception as e:
                print(e)
        

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

