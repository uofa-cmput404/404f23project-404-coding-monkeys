from django.test import TestCase, Client
from django.urls import reverse, resolve
from .models import AuthorUser, WhitelistController
from rest_framework import status
from accounts.views import SignUpView


#TO RUN ALL TESTS: python manage.py test
#TO RUN SPACIFIC TESTS: python manage.py test accounts

#see https://learndjango.com/tutorials/django-testing-tutorial and https://docs.djangoproject.com/en/4.2/topics/testing/overview/ 
#for examples of testing

class Author_Tests(TestCase):
    
    def setUp(self):# THIS MUST BE CALLED "setUp". It is case specific and will not be called it its named something other than "setUp"
        print("accounts/tests.py -> setUp commencing")#setUp will be run again for each test function below.

        
        #self.signup_url = reverse('signup')#Settup
        self.client = Client()#Settup
     
        WhitelistController.objects.create()
        
        #AuthorUser.objects.create(username='TestAuthor4', url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/800px-Banana-Single.jpg'
                                  #, github = 'https://github.com/NimaShariatz', password='ffafy1605', email='shariatz@ualberta.ca')
        
        self.user1 = AuthorUser.objects.create(
             username='BananaLover69',
             password='caffy1605',
             email='vroom@gmail.com',
             profile_image='https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/800px-Banana-Single.jpg',
             github='https://github.com/NimaShariatz'
            
        )
        
        
        

        
# Create your tests here.
    def test_author(self):
        print("accounts/tests.py -> test_author commencing")
        
        user_one= AuthorUser.objects.get(username="BananaLover69")
        
        
        self.assertEqual(user_one.username, "BananaLover69")
        self.assertEqual(user_one.password, "caffy1605")
        self.assertEqual(user_one.email, "vroom@gmail.com")
        self.assertEqual(user_one.profile_image, "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/800px-Banana-Single.jpg")
        self.assertEqual(user_one.github, "https://github.com/NimaShariatz")
        
        

    def test_login(self):
        print("accounts/tests.py -> test_login commencing")

        
        url = reverse('login')
        data_from_author= {'username': self.user1.username, 'password':self.user1.password}
        
        response = self.client.post(url, data_from_author)
        
        print(url)
        print(data_from_author)
        print(response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
