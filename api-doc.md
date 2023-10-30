# API Documentation

## Authors

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
**Request URL**: `http://service/api/authors/  
**Method:** GET  
**Description:** Returns a JSON-encoded list containing local author information  
**Example Response Body:**
```
{
    "type": "authors",
    "items": [
        {
            "type": "author",
            "id": "5",
            "host": "http://127.0.0.1:8000/",
            "displayName": "biguser2",
            "url": "http://127.0.0.1:8000/5/",
            "github": "https://github.com/uofa-cmput404/project-socialdistribution/",
            "profileImage": "https://wiki.teamfortress.com/w/images/4/4a/Pyroava.jpg"
        },
        {
            "type": "author",
            "id": "6",
            "host": "http://127.0.0.1:8000/",
            "displayName": "admin",
            "url": "http://127.0.0.1:8000/6/",
            "github": "https://docs.djangoproject.com/en/4.2/ref/contrib/auth/",
            "profileImage": "https://wiki.teamfortress.com/w/images/4/44/Sniperava.jpg"
        }
    ]
}
```

### View
**Request URL**: `http://service/api/authors/{id}/`  
**Method:** GET  
**Description:** Returns a single JSON-encoded object containing information for the provided author id.  
**Example Response Body:**
```
{
    "type": "author",
    "id": "5",
    "host": "http://127.0.0.1:8000/",
    "displayName": "biguser2",
    "url": "http://127.0.0.1:8000/5/",
    "github": "https://github.com/uofa-cmput404/project-socialdistribution/",
    "profileImage": "https://wiki.teamfortress.com/w/images/4/4a/Pyroava.jpg"
}
```


### Modify
**Request URL**: `http://service/api/authors/{id}/`  
**Method:** POST  
**Description:** Modify existing authors.  
**Example Request Body:**
```
{
    "type": "author",
    "id": "9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "host": "http://127.0.0.1:8000/",
    "displayName": "NewUsernameForMe",
    "url": "http://127.0.0.1:8000/9de17f29c12e8f97bcbbd34cc908f1baba40658e/",
    "github": "http://github.com/NewUsername",
    "profileImage": "https://wiki.teamfortress.com/w/images/4/4a/Pyroava.jpg"
}
```
