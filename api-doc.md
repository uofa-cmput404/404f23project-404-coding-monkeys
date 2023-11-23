# Remote API Documentation

## Table of Contents
---
[Authentication Cookie](#Authentication%20Cookie)
[Authors](#Authors)
[Followers](#Followers)
[Follow Requests](#Follow%20Requests)
[Posts](#Posts)
[Image Posts](#Image%20Posts)
[Comments](#Comments)
[Likes](#Likes)
[Liked](#Liked)
[Inbox](#Inbox)



## Notes
---
* `service` in our API calls will be represented by our public URI
* Most calls have:
	* `2XX` for success
	* `401` if authentication/cookie is required
	* `404` if the resource you are trying to access does not exist
	* `500` if a server error occurred



## Authentication Cookie
---
### Request Items  

| Key      | Description                   |  
| -------- | ----------------------------- |  
| user_id  | ID of the Author              |  
| username | Display name of the author    |  
| host     | Home host of the author       |  
| url      | URL to the author's profile   |  


Our webservice utilizes cookies to gather user information from remote servers. Typically, cookies should be re-assigned per request and only be active for a short period of time. To make your life easier, though, a cookie will only need to be established after a user successfully logs in to your server. This cookie is used to identify users for remote requests and will not need to be explicitly included in any of the API calls.

**Request URL**: `http://service/api/token/`
**Method**: POST
**Description**: POST to this URL after every successful authentication in your server. The request body contains information about the user who logged in.
**Example Request Body:**
```
{
	"user_id" : "1c946b62-e7ca-4d05-8f1d-8e25b6f214c5",
	"username" : "user1",
	"host" : "http://server",
	"url" : "http://server/authors/1c946b62-e7ca-4d05-8f1d-8e25b6f214c5"
}
```
**Example Response Body**:
```
{
  "message": "Succesfully set cookie."
}
```



## Authors
---
### Response Items
| Key           | Description                                         |
| ------------- | --------------------------------------------------- |
| type          | type of object, in our case "author"                                          |
| id            | ID of the Author |
| host          | the home host of the author |
| displayName   | the display name of the author         |
| url           | url to the author's profile |
| github        | HATEOS URL for Github API |
| profileImage  | Image from a public domain |

### List
**Request URL**: `http://service/authors/
**Method:** GET
**Description:** Returns a JSON-encoded list containing local author information
**Example Response Body:**
```
{
    "type": "authors",
    "items": [
        {
            "type": "author",
            "id": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
            "host": "http://127.0.0.1:8000/",
            "displayName": "biguser2",
            "url": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
            "github": "https://github.com/uofa-cmput404/project-socialdistribution",
            "profileImage": "https://wiki.teamfortress.com/w/images/4/4a/Pyroava.jpg"
        },
        {
            "type": "author",
            "id": "http://127.0.0.1:8000/4e1b44c9-2df6-4e2c-8a19-04a9d1b429c9",
            "host": "http://127.0.0.1:8000/",
            "displayName": "admin",
            "url": "http://127.0.0.1:8000/4e1b44c9-2df6-4e2c-8a19-04a9d1b429c9",
            "github": "https://docs.djangoproject.com/en/4.2/ref/contrib/auth",
            "profileImage": "https://wiki.teamfortress.com/w/images/4/44/Sniperava.jpg"
        }
    ]
}
```

### View
**Request URL**: `http://service/authors/{author_id}/`
**Method:** GET
**Description:** Returns a single JSON-encoded object containing information for the provided author id.
**Example Response Body:**
```
{
    "type": "author",
	"id": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
	"host": "http://127.0.0.1:8000/",
	"displayName": "biguser2",
	"url": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
	"github": "https://github.com/uofa-cmput404/project-socialdistribution",
	"profileImage": "https://wiki.teamfortress.com/w/images/4/4a/Pyroava.jpg"
}
```



## Followers
---
### List
**Request URL**: `http://service/authors/{author_id}/`
**Method:** GET
**Description:** Returns a list of authors who are following `author_id`.
**Example Response Body:**
```
{
	"type": "followers"
	"items": [
        {
            "type": "author",
            "id": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
            "host": "http://127.0.0.1:8000/",
            "displayName": "biguser2",
            "url": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
            "github": "https://github.com/uofa-cmput404/project-socialdistribution",
            "profileImage": "https://wiki.teamfortress.com/w/images/4/4a/Pyroava.jpg"
        },
        {
            "type": "author",
            "id": "http://127.0.0.1:8000/4e1b44c9-2df6-4e2c-8a19-04a9d1b429c9",
            "host": "http://127.0.0.1:8000/",
            "displayName": "admin",
            "url": "http://127.0.0.1:8000/4e1b44c9-2df6-4e2c-8a19-04a9d1b429c9",
            "github": "https://docs.djangoproject.com/en/4.2/ref/contrib/auth",
            "profileImage": "https://wiki.teamfortress.com/w/images/4/44/Sniperava.jpg"
        }
    ]
}
```



## Follow Requests
---
### Request Items
| Key           | Description                                         |
| ------------- | --------------------------------------------------- |
| type          | "Follow"                                          |
| summary            | summary of friend request |
| actor          | friend request sender |
| object   | friend request recipient         |


### Create
**Request URL**: `http://service/authors/{author_id}/inbox`
**Method:** POST
**Description:** Sends a follow request object to `author_id`'s inbox. `object` in the request is the receiver.
**Example Request Body:**
```
{
    "type": "Follow",      
    "summary":"Lara wants to follow Greg",
    "actor":{
        "type":"author",
        "id":"http://socialdistribution/authors/
		        9de17f29c12e8f97bcbbd34cc908f1baba40658e",
        "host":"http://socialdistribution/",
        "displayName":"Lara Croft",
        "url":"http://socialdistribution/authors/
		        9de17f29c12e8f97bcbbd34cc908f1baba40658e",
        "github": "http://github.com/laracroft",
        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
    },
    "object":{
        "type":"author",
        "id":"http://127.0.0.1:8000/authors/d5a40a82-d7cb-48f6-9436-14c2937a76f2",
        "url":"http://127.0.0.1:8000/authors/d5a40a82-d7cb-48f6-9436-14c2937a76f2",
        "host":"http://127.0.0.1:8000/",
        "displayName":"Greg Johnson",
        "github": "http://github.com/gjohnson",
        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
    }
}
    
```
**Example Response Body**: if the POST was successful, you should receive a `2XX` status and a response body that displays the newly created object (it should match the request body).



## Posts
---
### Response Items
| Key              | Description                                       |
| ---------------  | ------------------------------------------------- |
| type             | "post"                 |
| title            | title of the post                                  |
| id               | ID of the post (URL)                                    |
| source           | most recent source                   |
| origin           | original source                           |
| description      | a brief description of the post                    |
| contentType      | the content type of the post                        |
| content          | the content of the post                             |
| author           | information about the author                       |
| author.type      | type of object, in our case "author"               |
| author.id        | ID of the Author                                   |
| author.host      | the home host of the author                         |
| author.displayName| the display name of the author                      |
| author.url       | url to the author's profile                         |
| author.github    | HATEOS URL for Github API                          |
| author.profileImage| Image from a public domain |
| categories       | categories this post fits into (a list of strings) |
| count            | total number of comments for this post              |
| comments         | URL for the comments                  |
| commentsSrc      | we included this key, but we do not utilize it; it will always be `{}`     |
| published        | ISO 8601 TIMESTAMP for when the post was published |
| visibility       | visibility of the post ("PUBLIC", "FRIENDS", "PRIVATE")     |
| unlisted         | whether the post is unlisted (true/false)          |

### View
**Request URL**: `http://service/authors/{author_id}/posts/{post_id}/`
**Method:** GET
**Description:** Returns a single JSON-encoded object containing information for the provided post and author ID (if it exists and is permissible).
**Example Response Body:**
```
"type":"post",
    "title":"First Post",
	"id":"http://127.0.0.1:8000/authors/4e1b44c9-2df6-4e2c-8a19-
			04a9d1b429c9/posts/4e1b44c9-2df6-4e2c-8a19-04a9d1b429c9",
    "source":"http://lastplaceigotthisfrom.com/posts/yyyyy",
    "origin":"http://whereitcamefrom.com/posts/zzzzz",
    "description":"This post discusses stuff -- brief",
    "contentType":"text/plain",
    "content":"My first post!",
    "author": {
	    "type": "author",
		"id": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
		"host": "http://127.0.0.1:8000/",
		"displayName": "biguser2",
		"url": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
		"github": "https://github.com/uofa-cmput404/project-socialdistribution",
		"profileImage": "https://wiki.teamfortress.com/w/images/4/4a/Pyroava.jpg"
		},
    "categories":["web","tutorial"],
	"count": 1023
	"comments":"http://127.0.0.1:8000/authors/4e1b44c9-2df6-4e2c-8a19-
			04a9d1b429c9/posts/4e1b44c9-2df6-4e2c-8a19-04a9d1b429c9/comments",
    "commentsSrc": {},
    "published": "2015-03-09T13:07:04+00:00",
    "visibility": "PUBLIC",
    "unlisted": "false"
```

### List
**Request URL**: `http://service/authors/{author_id}/posts/?page=1&size=2
**Method:** GET
**Description:** Gets the recent posts from `author_id`. This call has **pagination** support.
**Example Response Body:**
```
{
	"type": "posts"
	"items": [
		{
			"type":"post",
		    "title":"First Post",
			"id":"http://127.0.0.1:8000/authors/4e1b44c9-2df6-4e2c-8a19-
					04a9d1b429c9/posts/4e1b44c9-2df6-4e2c-8a19-04a9d1b429c9",
		    "source":"",
		    "origin":"http://127.0.0.1:8000/authors/4e1b44c9-2df6-4e2c-8a19-
					04a9d1b429c9/posts/4e1b44c9-2df6-4e2c-8a19-04a9d1b429c9",
		    "description":"Here I am for the first time.",
		    "contentType":"text/plain",
		    "content":"My first post!",
		    "author": {
			    "type": "author",
				"id": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
				"host": "http://127.0.0.1:8000/",
				"displayName": "biguser2",
				"url": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
				"github": "https://github.com/uofa-cmput404/project-socialdistribution",
				"profileImage": "https://wiki.teamfortress.com/w/images/
						4/4a/Pyroava.jpg"
				},
		    "categories":["test"],
			"count": 523
			"comments":"http://127.0.0.1:8000/authors/4e1b44c9-2df6-4e2c-8a19-
					04a9d1b429c9/posts/4e1b44c9-2df6-4e2c-8a19-04a9d1b429c9/comments",
		    "commentsSrc": {},
		    "published": "2023-03-09T13:07:04+00:00",
		    "visibility": "PUBLIC",
		    "unlisted": "false"
	    },
	    {
			"type":"post",
		    "title":"Second Post",
			"id":"http://127.0.0.1:8000/authors/4e1b44c9-2df6-4e2c-8a19-
					04a9d1b429c9/posts/a52e39f4-aeb8-432c-9499-b36fc7da1a1a",
		    "source":"",
		    "origin":"http://127.0.0.1:8000/authors/4e1b44c9-2df6-4e2c-8a19-
					04a9d1b429c9/posts/a52e39f4-aeb8-432c-9499-b36fc7da1a1a",
		    "description":"Here I am again.",
		    "contentType":"text/plain",
		    "content":"My second post!",
		    "author": {
			    "type": "author",
				"id": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
				"host": "http://127.0.0.1:8000/",
				"displayName": "biguser2",
				"url": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
				"github": "https://github.com/uofa-cmput404/project-socialdistribution",
				"profileImage": "https://wiki.teamfortress.com/w/images/
						4/4a/Pyroava.jpg"
				},
		    "categories":[],
			"count": 2
			"comments":"http://127.0.0.1:8000/authors/4e1b44c9-2df6-4e2c-8a19-
					04a9d1b429c9/posts/a52e39f4-aeb8-432c-9499-b36fc7da1a1a/comments",
		    "commentsSrc": {},
		    "published": "2023-03-09T13:07:04+00:00",
		    "visibility": "PUBLIC",
		    "unlisted": "false"
	    },
	]
}
```


### Sending
**Request URL**: `http://service/authors/{author_id}/inbox
**Method:** POST
**Description:** Sends a post object to `author_id`'s inbox. 
**Example Request Body:**
```
{
	"type":"post",
    "title":"First Post",
	"id":"http://127.0.0.1:8000/authors/4e1b44c9-2df6-4e2c-8a19-
			04a9d1b429c9/posts/4e1b44c9-2df6-4e2c-8a19-04a9d1b429c9",
    "source":"http://lastplaceigotthisfrom.com/posts/yyyyy",
    "origin":"http://whereitcamefrom.com/posts/zzzzz",
    "description":"This post discusses stuff -- brief",
    "contentType":"text/plain",
    "content":"My first post!",
    "author": {
	    "type": "author",
		"id": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
		"host": "http://127.0.0.1:8000/",
		"displayName": "biguser2",
		"url": "http://127.0.0.1:8000/9d38f159-64f4-4ee3-9c4e-5232daa3c7b7",
		"github": "https://github.com/uofa-cmput404/project-socialdistribution",
		"profileImage": "https://wiki.teamfortress.com/w/images/4/4a/Pyroava.jpg"
		},
    "categories":["web","tutorial"],
	"count": 1023
	"comments":"http://127.0.0.1:8000/authors/4e1b44c9-2df6-4e2c-8a19-
			04a9d1b429c9/posts/4e1b44c9-2df6-4e2c-8a19-04a9d1b429c9/comments",
    "commentsSrc": {},
    "published": "2015-03-09T13:07:04+00:00",
    "visibility": "PUBLIC",
    "unlisted": "false"
   }
```
**Example Response Body**: if the POST was successful, you should receive a `2XX` status and a response body that displays the newly created object (it should match the request body).



## Image Posts
---
### View
**Request URL**: `http://service/authors/{author_id}/posts/{post_id}/image
**Method:** GET
**Description:** Gets the image associated with `post_id`, if one exists. This does not return a JSON object and merely returns the b64-encoded image data. Access the content type using the `content-type` header.
**Example Response Body:**
```
iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAFjAAABYwBQNL4DAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAACAASURBVHic7Z11lBzF1sB/I+su0Y27u3uAKIFAIGjQ4G4Plwc87MH7IFjQ4CSBQAiShLjLxm1jm41sNsm621h/f3SW2LSM9czs9u+cORxS1d13ZrtuVd26YkDHFeKA3kAfoCfQBGgEJALRQAhQBeSf/hwG9gK7gNVApvYiByVRwGCgF9AJaAvUB5KB2NN9ioBK4ARwEtgP7AA2Agc0llenFtMYeBBYBdgBwYPPIeBdYCBg0PJLBAFNgEcRFaUVz37nDOBDYJCm30CnVnERMB/PB73UZx/wEBCj1RcKQAzAGOAPfPc7H0BU4NEafSedIMYAXAVsxjcvo7NPHvA0EKnB9wskxgCpaPc7FwDPoysCHQl6ACvR7oU8/3MIcVDUdlKAX/Hf73wKuBsw+vqL6gQHccDHgA3/vZRnf75HNHjVNozA/UAx/v+NBWADotLXqcMMBNLx/8t4/icHGOG7r605scBv+P93Pf9jBd5EPL2pk9RVS3Qo8DLwL8Dkzg3MIWaad2hMYoM44urFEBMvbi3LiysoL6kgN6uAExk5lBVXuCujBdF49Zm7NwgQOiIO/nbuXGwyG2nYvB71myaR1DAec6iZiKhwqqssFOeWUJhbwolD2RTllXoi43rgeuCoJzcJRuqiAmiAuAd1+YioadtGDL2iD92GdKBVlyaYQ8yy/QVB4Hj6KdI2prNx4Q52rduP3eZw9bH/BzyBOGMFG8MQLfyxSh3P...
```



### Comments
---
### Request/Response Items
| Key          | Description                                       |
| ------------ | ------------------------------------------------- |
| type         | type of object, in our case "comments"             |
| page         | page number of the comments                        |
| size         | number of comments per page                        |
| post         | URL of the post associated with the comments       |
| id           | URL of the comments                                |
| comments     | list of comments                                   |
| comments.type| type of object, in our case "comment"              |
| comments.author| information about the comment's author            |
| comments.author.type| type of object, in our case "author"           |
| comments.author.id| ID of the Comment Author                          |
| comments.author.url| URL to the author's information                   |
| comments.author.host| Home host of the author                           |
| comments.author.displayName| Display name of the author                |
| comments.author.github | HATEOS URL for Github API                    |
| comments.author.profileImage | Image from a public domain |
| comments.comment| the content of the comment                         |
| comments.contentType| the content type of the comment                |
| comments.published| ISO 8601 TIMESTAMP for when the comment was published |
| comments.id   | ID of the comment                                  |

### List
**Request URL**: `http://service/authors/{author_id}/posts/{post_id}/comments?page=1&size=2
**Method:** GET
**Description:** Gets the list of comments of the post whose id is `post_id`. This call has **pagination** support.
**Example Response Body:**
```
{
    "type":"comments",
    "page":1,
    "size":5,
	"post":"http://127.0.0.1:5454/authors/a02e3525-bb5a-44eb-852d-
			0f93f63d1a2c/posts/3d9f1a06-0d98-4466-9f64-8b79d97325db"
	"id":"http://127.0.0.1:5454/authors/a02e3525-bb5a-44eb-852d-
			0f93f63d1a2c/posts/3d9f1a06-0d98-4466-9f64-8b79d97325db/comments"
    "comments":[
        {
            "type":"comment",
            "author":{
                "type":"author",
                "id":"http://127.0.0.1:8000/authors/48002331-c8fa-4947-a012-
		                a2a8bafeff12",
                "url":"http://127.0.0.1:8000/authors/48002331-c8fa-4947-a012-
		                a2a8bafeff12",
                "host":"http://127.0.0.1:8000/",
                "displayName":"Skittles",
                "github": "http://github.com/skittlz",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            },
            "comment":"I like skittles",
            "contentType":"text/plaintext",
            "published":"2023-03-09T13:07:04+00:00",
            "id":"http://127.0.0.1:5454/authors/a02e3525-bb5a-44eb-852d-
					0f93f63d1a2c/posts/3d9f1a06-0d98-4466-9f64-8b79d97325db/comments/
					e6e04955-63a7-445f-a97e-aaab143e73ea",
        },
        {
            "type":"comment",
            "author":{
                "type":"author",
                "id":"http://127.0.0.1:8000/authors/6d44a8df-dc0b-44a1-b3a0-
		                1f6939a949ca",
                "url":"http://127.0.0.1:8000/authors/6d44a8df-dc0b-44a1-b3a0-
		                1f6939a949ca",
                "host":"http://127.0.0.1:8000/",
                "displayName":"Greg Johnson",
                "github": "http://github.com/gjohnson",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            },
            "comment":"Nice dude",
            "contentType":"text/plaintext",
            "published":"2023-04-09T13:07:04+00:00",
            "id":"http://127.0.0.1:5454/authors/a02e3525-bb5a-44eb-852d-
					0f93f63d1a2c/posts/3d9f1a06-0d98-4466-9f64-8b79d97325db/comments/
					c1eb1d0a-3300-433c-b5dc-740248c764c1",
        }
    ]
}
    
```


### Create
**Request URL**: `http://service/authors/{author_id}/inbox
**Method:** POST
**Description:** Sends a comment object to `author_id`'s inbox. Creates the object.
**Example Request Body:**
```
{
      "type": "comment",
      "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/authors/7bdcfebf-6870-461b-b9ff-4f75f938f4e1",
        "url": "http://127.0.0.1:8000/authors/7bdcfebf-6870-461b-b9ff-4f75f938f4e1",
        "host": "http://127.0.0.1:8000/",
        "github": "https://github.com/sudo",
        "displayName": "sudo",
        "profileImage": "https://wiki.teamfortress.com/w/images/thumb/0/0f/
		        Meet_the_Heavy_SFM.png/550px-Meet_the_Heavy_SFM.png"
      },
      "comment": "hmmmmm",
      "contentType": "text/plain",
      "published": "2023-11-21 04:34:24.883929+00:00",
      "id": "http://127.0.0.1:8000/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/
		      posts/adsigjdoasig/comments/35f9bb9c-9b3f-4029-8592-05f6db3b4018"
}
```
**Example Response Body**: if the POST was successful, you should receive a `2XX` status and a response body that displays the newly created object (it should match the request body).



## Likes
---
### Request/Response Items
| Key           | Description                                         |
| ------------- | --------------------------------------------------- |
| type          | "Like"                                          |
| summary            | summary of like |
| context          | context of like (URL) |
| author   | author sending like         |
| object   | the liked object (URL to a post or comment)         |

### Create
**Request URL**: `http://service/authors/{author_id}/inbox`
**Method:** POST
**Description:** Sends a like object to `author_id`'s inbox. Creates the object.
**Example Request Body:**
```
 {
     "context": "https://www.w3.org/ns/activitystreams",
     "summary": "Lara Croft Likes your post",         
     "type": "Like",
     "author":{
         "type":"author",
         "id":"http://remote/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
         "host":"http://remote/",
         "displayName":"Lara Croft",
         "url":"http://remote/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
         "github":"http://github.com/laracroft",
         "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
     },
     "object":"http://127.0.0.1:8000/authors/6d44a8df-dc0b-44a1-b3a0-
		     1f6939a949ca/posts/c3b38515-d6da-4c23-9df1-15ac4be5d929"
}
```
**Example Response Body**: if the POST was successful, you should receive a `2XX` status and a response body that displays the newly created object (it should match the request body).


### Post Likes
<mark style="background: #FF5582A6;">Still in progress</mark>
**Request URL**: `http://service/authors/{author_id}/posts/{post_id}/likes`
**Method:** GET
**Description:** Retrieves a list of likes from other authors on `author_id`'s post `post_id`


### Comment Likes
<mark style="background: #FF5582A6;">Still in progress</mark>
**Request URL**: `http://service/authors/{author_id}/posts/{post_id}/comments/{comment_id}/likes`
**Method:** GET
**Description:** Retrieves a list of likes from other authors on `author_id`’s post `post_id` comment `comment_id`



### Liked
---
### List
<mark style="background: #FF5582A6;">Still in progress</mark>
**Request URL**: `http://service/authors/{author_id}/liked
**Method:** GET
**Description:** Retrieves the list of public things that `author_id` has liked.



## Inbox
---
Likes, comments, and follow requests sent to an author's inbox will create those objects and notify the user. Shared posts, however, will only notify the user; foreign posts are not stored, but should be retrievable for a user's timeline through the posts API.
![](Pasted%20image%2020231122120126.png)

Reference the following documentation for sending each item:
[Likes](#Likes#Create)
[Comments](#Create)
[Follow Requests](#Follow%20Requests#Create)
[Posts](#Posts#Sending)





