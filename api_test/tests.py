from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import BlogPost

class BlogPostTests(APITestCase):
	def test_create_blogpost(self):
		"""
		Ensure we can create a new blog post.
		"""
		url = reverse('api_test:blogpost-list')
		data = {'title': 'Test Post', 'content': 'Test content'}
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(BlogPost.objects.count(), 1)
		self.assertEqual(BlogPost.objects.get().title, 'Test Post')