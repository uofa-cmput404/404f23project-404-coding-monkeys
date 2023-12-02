import uuid
import json

post_uuid = uuid.uuid4()
author_uuid = "a02e3525-bb5a-44eb-852d-0f93f63d1a22" # TestUser1_dev

put_data = {
    "type": "post",
    "title": "A post title about a post about web dev",
    "id": f"http://127.0.0.1:8000/authors/{author_uuid}/posts/{post_uuid}",
    "source": "http://lastplaceigotthisfrom.com/posts/yyyyy",
    "origin": "http://whereitcamefrom.com/posts/zzzzz",
    "description": "test post",
    "contentType": "text/plain",
    "content": "PUT Post local api call working",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/authors/{author_uuid}",
        "host": "http://127.0.0.1:8000/",
        "displayName": "TestUser1",
        "url": "http://127.0.0.1:8000/authors/{author_uuid}",
        "github": "http://github.com/test1",
        "profileImage": "https://avatars.akamai.steamstatic.com/c718b0c234a3f5ff5fc8f0b99c3f64f0de4ccefe_full.jpg"
    },
    "categories": ["web", "tutorial"],
    "count": 0,
    "comments": f"http://127.0.0.1:8000/authors/{author_uuid}/posts/{post_uuid}/comments",
    "commentsSrc": {

    },
    "published": "2015-03-09T13:07:04+00:00",
    "visibility": "PUBLIC",
    "unlisted": False
}

print(f"curl -X PUT -u 'TestUser1_dev:helloPassword7&' http://127.0.0.1:8000/authors/{author_uuid}/posts/{post_uuid}/  -H 'Content-Type: application/json' -d '{json.dumps(put_data)}' -v")