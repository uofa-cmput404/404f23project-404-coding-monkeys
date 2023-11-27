from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import AuthorUser, WhitelistController#Import this in particular. BTW theres nothing in pages/views.py and we have to use authors.models.py instead for testing the pages here
from rest_framework import status

#TO RUN ALL TESTS: python manage.py test
#TO RUN SPACIFIC TESTS: python manage.py test pages


class Author_Tests(TestCase):
    
    def setUp(self):# THIS MUST BE CALLED "setUp". It is case specific and will not be called it its named something other than "setUp"
        print("pages/tests.py -> setUp commencing")#setUp will be run for each test function below.

        self.client = Client()#Settup


        WhitelistController.objects.create()
        
        self.user1 = AuthorUser.objects.create(
             username='BananaLover69',
             password='caffy1605',
             email='vroom@gmail.com',
             profile_image='https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/800px-Banana-Single.jpg',
             github='https://github.com/NimaShariatz'
            
        )
        
    def test_allAuthorsURL(self):
        url = reverse('authors_list')#This test is incomplete. continue from here
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)