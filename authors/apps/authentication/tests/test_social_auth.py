from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
import os
from django.urls import reverse
import json


class SocialAuthTest(APITestCase):
    """This class test social logins"""

    def setUp(self):

        self.client = APIClient()
        self.social_auth_url = '/api/social_auth'
        self.invalid_token = {
            "provider": "google-oauth2",
            "access_token": "invalid-token"
        }

        self.invalid_provider = {
            "provider": "invalid-provider",
            "access_token": "@#JOEJO@()#)!(JKJEWQKL@#",
        }
        self.missing_token = {
            "provider": "twitter",
        }

        self.twitter_data = {
            "provider": "twitter",
            "access_token": os.getenv('TWITTER_ACCESS_TOKEN'),
            "access_token_secret": os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
        }

        self.facebook_data = {
            "provider": "twitter",
            "access_token": os.getenv('FB_ACCESS_TOKEN'),
        }
        self.google_data = {
            "provider": "twitter",
            "access_token": os.getenv('GOOGLE_ACCESS_TOKEN'),
        }

    # def test_invalid_token(self):
    #     """Test response when token is invalid"""
    #     data = self.invalid_token
    #     url = self.social_auth_url
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_missing(self):
        """Test response when token is invalid"""
        data = self.missing_token
        url = self.social_auth_url
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_provider(self):
        """Test response when user uses an invalid provider"""
        data = self.invalid_provider
        url = self.social_auth_url
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_twitter(self):
        """Test login/signup using twitter keys"""
        url = self.social_auth_url
        data = self.twitter_data
        response = self.client.post(url, data=data, format='json')
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', data["user"])
        self.assertIn('email', data["user"])

    # def test_login_with_facebook(self):
    #     """Test login/signup using twitter keys"""
    #     url = self.social_auth_url
    #     data = self.facebook_data
    #     response = self.client.post(url, data=data, format='json')
    #     data = json.loads(response.content)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_login_with_google(self):
    #     """Test login/signup using twitter keys"""
    #     url = self.social_auth_url
    #     data = self.google_data
    #     response = self.client.post(url, data=data, format='json')
    #     data = json.loads(response.content)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
