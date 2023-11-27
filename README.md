CMPUT404-project-socialdistribution
===================================

CMPUT 404 Project: Social Distribution

[Project requirements](https://github.com/uofa-cmput404/project-socialdistribution/blob/master/project.org) 

Contributors / Licensing
========================

Authors:
    
* Nima Shariatzadeh(shariatz@ualberta.ca)
* Aidan Lynch(alynch1@ualberta.ca)
* Sophia Ruduke(sruduke@ualberta.ca)
* Matthew Wood(mwood2@ualberta.ca)
* Davicheanin Meas(meas@ualberta.ca)

Running Instructions (on the lab machines):
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

Operating Instructions:
* To log in for the first time, visit `http://127.0.0.1:8000`
* Posts:
    * To see the posts on your feed, visit `http://127.0.0.1:8000/posts/stream/`
    * To create a post, visit `http://127.0.0.1:8000/posts/new/`
* To see a list of the users, visit `http://127.0.0.1:8000/authors/`

Helpful info for testing:
User Logins:
* Username: TestUser1, Password: helloPassword7&
* Username: TestUser2, Password: helloPassword7&

Helpful info for Database Development:
* Content types:
    * Plain text: `"text/plain"` -- UTF-8
    * Markdown text: `"text/markdown"`-- common mark
    * Images:
        * png: `"image/png;base64"` -- images are POSTS. So you might have a user make 2 posts if a post includes an image!
        * jpeg: `"image/jpeg;base64"`
    * Other Data: `"application/base64"`



Generally everything is LICENSE'D under the MIT License.

============================================================
See DFB pg. 58; reconfigured settings file so all templates can be placed in root /templates/ directory, instead of needing a separate templates folder for every app.
