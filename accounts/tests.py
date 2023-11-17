from django.test import TestCase, Client
from django.urls import reverse, resolve
from .models import AuthorUser
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
     
        
        
        #AuthorUser.objects.create(username='TestAuthor4', url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/800px-Banana-Single.jpg'
                                  #, github = 'https://github.com/NimaShariatz', password='ffafy1605', email='shariatz@ualberta.ca')
        
        self.user1 = AuthorUser.objects.create(
             username='testUser1',
             password='caffy1605',
             email='vroom@gmail.com',
             github='https://github.com/NimaShariatz'
            
        )
        
        
        
        
# Create your tests here.
    def test_author(self):
        print("accounts/tests.py -> test_author commencing")