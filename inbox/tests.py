from django.test import TestCase

# Create your tests here.
post_body = {
  "type": "test",
  "title": "This field is required.",
  "id": "This field is required.",
  "source": "This field is required.",
  "origin": "This field is required.",
  "description": "This field is required.",
  "contentType": "plaintext",
  "content": "This field is required.",
  "author": {
    "type": "author",
    "username": "sudo",
    "profile_image": ":)"
  },
  "categories": [
    "c1",
    "c2"
  ],
  "comments": "This field is required.",
  "published": "2023-11-27T12:20:22",
  "visibility": "FRIENDS",
  "unlisted": False
}