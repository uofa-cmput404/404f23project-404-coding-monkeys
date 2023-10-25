from django.test import TestCase
from django.urls import reverse
from accounts.models import AuthorUser#Import this in particular. BTW theres nothing in pages/views.py and we have to use authors.models.py instead for testing the pages here

from pages.views import follow_author# for def test_follow(self)

#TO RUN ALL TESTS: python manage.py test
#TO RUN SPACIFIC TESTS: python manage.py test pages


class Author_Tests(TestCase):
    
    def setUp(self):# THIS MUST BE CALLED "setUp". It is case specific and will not be called it its named something other than "setUp"
        print("pages/tests.py -> setUp commencing")#setUp will be run for each test function below.

        #Do this to create the users or objects
        AuthorUser.objects.create(username='TestAuthor1')
        
        AuthorUser.objects.create(username='TestAuthor2', url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/800px-Banana-Single.jpg')
                
        AuthorUser.objects.create(username='TestAuthor3', github = 'https://github.com/NimaShariatz')        
        
        AuthorUser.objects.create(username='TestAuthor4', url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/800px-Banana-Single.jpg'
                                  , github = 'https://github.com/NimaShariatz', password='ffafy1605' )

# Create your tests here.
    def test_link(self): #WE ARE TESTING: http://127.0.0.1:8000/authors/<PK>/ stuff here
        print("pages/tests.py -> test_link commencing")
        
        #---check account 1---
        user_one = AuthorUser.objects.get(id=1) #the PK ids are 1 to 4 since in this fake database, we only have 4 users
                                                #so obviously their PKs are in the order that we make them
        self.assertEqual(user_one.username, "TestAuthor1")#making sure PK 1 is TestAuthor1
        
        response1 = self.client.get("/authors/1/")
        self.assertEqual(response1.status_code, 200)
        response1 = self.client.get(reverse("author_profile", args=[1]))#set args to our <int:pk> which is 1, since we are testing account 1
        self.assertEqual(response1.status_code, 200)
        self.assertTemplateUsed(response1, "authorprofile.html")
        
        response1 = self.client.get("/authors/1/editprofile/")
        self.assertEqual(response1.status_code, 200)
        response1 = self.client.get(reverse("author_edit", args=[1]))#set args to our <int:pk> which is 1, since we are testing account 1
        self.assertEqual(response1.status_code, 200)
        self.assertTemplateUsed(response1, "editprofile.html")
        
        #response1 = self.client.get("/authors/1/followed/") URL DOES NOT WORK YET
        #self.assertEqual(response1.status_code, 200)
        
        response1 = self.client.get("/authors/1/followrequests/")
        self.assertEqual(response1.status_code, 200)
        response1 = self.client.get(reverse("author_requests", args=[1]))#set args to our <int:pk> which is 1, since we are testing account 1
        self.assertEqual(response1.status_code, 200)
        self.assertTemplateUsed(response1, "followrequests.html")
        


        
        
        
                    
        #---check account 2---
        user_two = AuthorUser.objects.get(id=2)
        self.assertEqual(user_two.username, "TestAuthor2")#making sure PK 2 is TestAuthor2
        

        response2 = self.client.get("/authors/2/")
        self.assertEqual(response2.status_code, 200)
        response2 = self.client.get(reverse("author_profile", args=[2]))#set args to our <int:pk> which is 2, since we are testing account 1
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "authorprofile.html")
        
        
        response2 = self.client.get("/authors/2/editprofile/")
        self.assertEqual(response2.status_code, 200)
        response2 = self.client.get(reverse("author_edit", args=[2]))#set args to our <int:pk> which is 2, since we are testing account 1
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "editprofile.html")
        
        #response2 = self.client.get("/authors/2/followed/") URL DOES NOT WORK YET
        #self.assertEqual(response2.status_code, 200)
        
        response2 = self.client.get("/authors/2/followrequests/")
        self.assertEqual(response2.status_code, 200)
        response2 = self.client.get(reverse("author_requests", args=[2]))#set args to our <int:pk> which is 2, since we are testing account 1
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "followrequests.html")
        
        #---check account 3---
        user_three = AuthorUser.objects.get(id=3)
        self.assertEqual(user_three.username, "TestAuthor3")#making sure PK 3 is TestAuthor3
        

        response3 = self.client.get("/authors/3/")
        self.assertEqual(response3.status_code, 200)
        response3 = self.client.get(reverse("author_profile", args=[3]))#set args to our <int:pk> which is 3, since we are testing account 1
        self.assertEqual(response3.status_code, 200)
        self.assertTemplateUsed(response3, "authorprofile.html")
        
        response3 = self.client.get("/authors/3/editprofile/")
        self.assertEqual(response3.status_code, 200)
        response3 = self.client.get(reverse("author_edit", args=[3]))#set args to our <int:pk> which is 3, since we are testing account 1
        self.assertEqual(response3.status_code, 200)
        self.assertTemplateUsed(response3, "editprofile.html")
        
        #response3 = self.client.get("/authors/3/followed/") URL DOES NOT WORK YET
        #self.assertEqual(response3.status_code, 200)
        
        response3 = self.client.get("/authors/3/followrequests/")
        self.assertEqual(response3.status_code, 200)
        response3 = self.client.get(reverse("author_requests", args=[3]))#set args to our <int:pk> which is 3, since we are testing account 1
        self.assertEqual(response3.status_code, 200)
        self.assertTemplateUsed(response3, "followrequests.html")
        
        
        #---check account 4---
        user_four = AuthorUser.objects.get(id=4)
        self.assertEqual(user_four.username, "TestAuthor4")#making sure PK 4 is TestAuthor4
        

        response4 = self.client.get("/authors/4/")
        self.assertEqual(response4.status_code, 200)
        response4 = self.client.get(reverse("author_profile", args=[4]))#set args to our <int:pk> which is 3, since we are testing account 1
        self.assertEqual(response4.status_code, 200)
        self.assertTemplateUsed(response4, "authorprofile.html")
        
        response4 = self.client.get("/authors/4/editprofile/")
        self.assertEqual(response4.status_code, 200)
        response4 = self.client.get(reverse("author_edit", args=[4]))#set args to our <int:pk> which is 3, since we are testing account 1
        self.assertEqual(response4.status_code, 200)
        self.assertTemplateUsed(response4, "editprofile.html")
        
        #response4 = self.client.get("/authors/4/followed/") URL DOES NOT WORK YET
        #self.assertEqual(response4.status_code, 200)
        
        response4 = self.client.get("/authors/4/followrequests/")
        self.assertEqual(response4.status_code, 200)
        response4 = self.client.get(reverse("author_requests", args=[4]))#set args to our <int:pk> which is 3, since we are testing account 1
        self.assertEqual(response4.status_code, 200)
        self.assertTemplateUsed(response4, "followrequests.html")
        

    def test_follow(self):
        print("pages/tests.py -> test_follow commencing")

                #TO-DO!!
        #---THE FOLLOWING BELOW WILL TEST THE "FOLLOWING" FEATURE---
        
        #so when path("authors/<int:pk>/followed/", views.follow_author, name="author_followed"), is called, it will trigger the model
        #follow_author view in pages/views.py
        
        #when follow_author is triggered in views.py, its going to get the current user in the account and their data and makes a dictionary, 
        #then get the information of whom you are trying to follow and their data and makes a dictionary
        
        #and it makes a print statement of who wants to follow who
        
        #When the user accepts or denies a request, it quickly changes URL links to either 
        #    path("authors/<int:pk>/followrequests/accept/<int:fq_pk>", views.accept_fq, name="fq_accept"),
        # OR
        #    path("authors/<int:pk>/followrequests/deny/<int:fq_pk>", views.deny_fq, name="fq_deny"),
        
        #So step 1. work with follow_author from views.py to make a follow request
        
        #AuthorUser.objects.follow
        