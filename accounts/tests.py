from django.test import TestCase
from django.urls import reverse
from .models import AuthorUser#Import this in particular

#TO RUN ALL TESTS: python manage.py test
#TO RUN SPACIFIC TESTS: python manage.py test accounts

#see https://learndjango.com/tutorials/django-testing-tutorial and https://docs.djangoproject.com/en/4.2/topics/testing/overview/ 
#for examples of testing

class Author_Tests(TestCase):
    
    def setUp(self):# THIS MUST BE CALLED "setUp". It is case specific and will not be called it its named something other than "setUp"
        print("accounts/tests.py -> setUp commencing")#setUp will be run again for each test function below.

        #Do this to create the users or objects
        AuthorUser.objects.create(username='TestAuthor1')
        
        AuthorUser.objects.create(username='TestAuthor2', url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/800px-Banana-Single.jpg')
                
        AuthorUser.objects.create(username='TestAuthor3', github = 'https://github.com/NimaShariatz')        
        
        AuthorUser.objects.create(username='TestAuthor4', url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/800px-Banana-Single.jpg'
                                  , github = 'https://github.com/NimaShariatz', password='ffafy1605' )
# Create your tests here.
    def test_author(self):
        print("accounts/tests.py -> test_author commencing")
        
        user_one= AuthorUser.objects.get(username="TestAuthor1")
        user_two = AuthorUser.objects.get(username="TestAuthor2")
        user_three = AuthorUser.objects.get(username="TestAuthor3")
        user_four = AuthorUser.objects.get(username="TestAuthor4")

        
        self.assertEqual(user_one.username, "TestAuthor1")
        self.assertEqual(user_one.password, "")
        self.assertEqual(user_one.url, "")
        self.assertEqual(user_one.github, None)
        
        self.assertEqual(user_two.username, "TestAuthor2")
        self.assertEqual(user_two.password, "")
        self.assertEqual(user_two.url, "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/800px-Banana-Single.jpg")
        self.assertEqual(user_two.github, None)


        self.assertEqual(user_three.username, "TestAuthor3")
        self.assertEqual(user_three.password, "")
        self.assertEqual(user_three.url, "")
        self.assertEqual(user_three.github, "https://github.com/NimaShariatz")
        
        self.assertEqual(user_four.username, "TestAuthor4")
        self.assertEqual(user_four.password, "ffafy1605")
        self.assertEqual(user_four.url, "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/800px-Banana-Single.jpg")
        self.assertEqual(user_four.github, "https://github.com/NimaShariatz")
        
        
    def test_link(self):#http://127.0.0.1:8000/accounts/signup/
        
        print("accounts/tests.py -> test_link commencing")
        response1 = self.client.get("/accounts/signup/")
        self.assertEqual(response1.status_code, 200)
        
        response2 = self.client.get(reverse("signup"))#"signup" comes from the name given to the URL at accounts/urls.py
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "registration/signup.html")#checks if the HTML page used is this one.