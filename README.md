Chimp Chat: CMPUT404-project-socialdistribution
===================================

### Information
**Group Name:** `Coding Monkeys`  
**CMPUT 404 Project Name:** `Chimp Chat`

**Description:** Chimp Chat is a social media platform that allows you to create and share posts with your friends.
Unlike traditional social platforms, Chimp Chat is able to interface with other platforms through its API, allowing for interaction between users of different services.

Created with Django.

### Demo Video
[![IMAGE ALT TEXT HERE](https://i.imgur.com/3tGj4pW.png)](https://www.youtube.com/watch?v=8FuEcxVs9IE)

### Links
[Public URI](https://chimp-chat-1e0cca1cc8ce.herokuapp.com/)  
[API Documentation](https://chimp-chat-1e0cca1cc8ce.herokuapp.com/api/)  
[Project requirements](https://github.com/uofa-cmput404/project-socialdistribution/blob/master/project.org) 

<br>

## Contributors / Licensing

Authors:
    
* Nima Shariatzadeh shariatz@ualberta.ca
* Aidan Lynch alynch1@ualberta.ca
* Sophia Ruduke sruduke@ualberta.ca
* Matthew Wood mwood2@ualberta.ca
* Davin meas@ualberta.ca - **Joined November 3rd, 2023**

<br> 

Generally everything is LICENSE'D under the MIT License.

<br></br>

## Public Users
```
Username: TestUser1
Password: helloPassword7&

Username: TestUser2
Password: helloPassword7&
```

<br>

## Group Connections

### 404 Not Found
Login link: https://distributed-network-37d054f03cf4.herokuapp.com/login/
```
username: sophisdope
password: hahaha13
```

Link to API docs: https://documenter.getpostman.com/view/29719988/2s9Ye8hFfD/
```
username (for api): node-code-monkeys
password (for api): node-code-monkeys
```

Connectivity: Fully connected.

<br>

### Web Wizards
Login link: https://uofa-cmput404.github.io/404f23project-web-wizards/login
```
username: node-code-monkeys
password: socialpassword
```

Link to API docs: https://webwizards-backend-952a98ea6ec2.herokuapp.com/doc/
```
username (for api): node-code-monkeys
password (for api): socialpassword
```

Connectivity: Can view their authors and posts on our site, but cannot interact with them.

<br>

### Ctrl-Alt-Defeat
Login Link: https://cmput404-ctrl-alt-defeat-react-574ccb97869b.herokuapp.com/
```
Username: localhost
Password: test
```

Link to API docs: https://cmput404-ctrl-alt-defeat-api-12dfa609f364.herokuapp.com/api/docs/
```
username (for api): CodingMonkeys
password (for api): password
```

Connectivity: Everything but commenting and sharing posts.

<br>

### A-Team
Login Link: https://c404-5f70eb0b3255.herokuapp.com/
```
Username: coding-monkeys-demo
Password: password
```

Link to API docs: https://c404-5f70eb0b3255.herokuapp.com/swagger/
```
Token Auth: 5e21ab2cfbadeebe869c6c57efe9535c4b79e0d7
```

Connectivity: Can see their authors and posts on our site, but cannot interact with them.

<br>

## User Stories

### The following is the user stories implemented within the given timeframe.
- [x] As an author I want to make public posts.
- [x] As an author I want to edit public posts.
- [x] As an author, posts I create can link to images.
- [x] As an author, posts I create can be images.
- [x] As a server admin, images can be hosted on my server.
- [ ] As an author, posts I create can be private to another author. `posts can only be private to followers`
- [x] As an author, posts I create can be private to my friends.
- [x] As an author, I can share other author’s public posts.
- [x] As an author, I can re-share other author’s friend posts to my friends.
- [x] As an author, posts I make can be in simple plain text.
- [x] As an author, posts I make can be in CommonMark.
- [x] As an author, I want a consistent identity per server.
- [x] As a server admin, I want to host multiple authors on my server.
- [x] As a server admin, I want to share public images with users on other servers.
- [x] As an author, I want to pull in my GitHub activity to my “stream”. `available on the author profile page`
- [x] As an author, I want to post posts to my “stream”.
- [x] As an author, I want to delete my own public posts.
- [x] As an author, I want to befriend local authors.
- [x] As an author, I want to befriend remote authors.
- [x] As an author, I want to feel safe about sharing images and posts with my friends – images shared to friends should only be visible to friends. `public images are public; all images and APIs are only shared with those who should have access`
- [x] As an author, when someone sends me a friends-only post I want to see the likes.
- [x] As an author, comments on friend posts are private only to me, the original author.
- [ ] As an author, I want to unfriend local and remote authors `this is functional but isn't pretty on local; uncertain about remote`
- [x] As an author, I want to be able to use my web browser to manage my profile.
- [x] As an author, I want to be able to use my web browser to manage/author my posts.
- [x] As a server admin, I want to be able to add, modify, and remove authors.
- [x] As a server admin, I want to OPTIONALLY be able to allow users to sign up but require my OK to finally be on my server.
- [x] As a server admin, I don’t want to do heavy setup to get the posts of my author’s friends.
- [x] As a server admin, I want a restful interface for most operations.
- [x] As an author, other authors cannot modify my public post.
- [x] As an author, other authors cannot modify my shared-to-friends post.
- [x] As an author, I want to comment on posts that I can access.
- [x] As an author, I want to like posts that I can access.
- [x] As an author, my server will know about my friends.
- [ ] As an author, when I befriend someone (they accept my friend request) I follow them, only when the other author befriends me do I count as a real friend – a bi-directional follow is a true friend.
- [x] As an author, I want to know if I have friend requests. `available in inbox`
- [x] As an author I should be able to browse the public posts of everyone. `found in explore tab`
- [x] As a server admin, I want to be able to add nodes to share with.
- [x] As a server admin, I want to be able to remove nodes and stop sharing with them.
- [x] As a server admin, I can limit nodes connecting to me via authentication.
- [x] As a server admin, node-to-node connections can be authenticated with HTTP Basic Auth.
- [x] As a server admin, I can disable the node-to-node interfaces for connections that are not authenticated!
- [x] As an author, I want to be able to make posts that are unlisted, that are publicly shareable by URI alone (or for embedding images).


<br>

## Operation

### Note
This project will not run OOB since the Django `settings.py` must be configured in the `django_project/` directory. To connect to our Postgres development database, two static configuration files will need to be added to the project using:  

`git checkout dev && git pull && git checkout main && git checkout dev -- static/vars.py django_project/settings.py`  

<br>

Operation of this web application using this method will only be valid for the time of the project; the credentials will be obsolete after the marking period for the security and maintenance of our web application. In that case, the project can still be run locally using the [default settings file](https://docs.djangoproject.com/en/4.2/topics/settings/) from the Django documentation and creating a SQLite3 database.

<br>

### Running Instructions (on the lab machines):
* Create venv:
    * `python3 -m venv codingMonkeysEnv`
    * `source codingMonkeysEnv/bin/activate`
* Install Requirements:
    * `pip install -r requirements.txt`
    * You may see an error for "Building wheel for svglib", that is okay
* Run the project:
    * `python3 manage.py runserver`
    * This will start a webserver on the lab machine's `localhost:8000`
        * If you are SSH-ing into the lab machine, you will need to forward this port in order to see the site on your device. Vscode makes this very easy.
* To deactivate the web server, simply hit `ctrl-c` in the terminal.

### Operating Instructions:
* To log in for the first time, visit `http://127.0.0.1:8000`
* Posts:
    * To see the posts on your feed, visit `http://127.0.0.1:8000/posts/stream/`
    * To create a post, visit `http://127.0.0.1:8000/posts/new/`
* To see a list of the users, visit `http://127.0.0.1:8000/authors/`

### API Testing  
We utilized the open-source API testing software called [Bruno](https://www.usebruno.com/downloads) to automate and run our API tests. If you wish to run the API tests, simply download Bruno and open the `api_testing` directory as a collection; ensure to set the testing environment to the one included in the collection. These tests can only be run on a `localhost` instance using the current testing environment; however, the URI can be changed to the public URI and tests can be adapted to run it on the public site.

<br>


