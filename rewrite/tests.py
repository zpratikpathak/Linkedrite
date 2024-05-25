from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from .models import APICounter


class RewriteAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse(
            "rewrite"
        )  # replace 'rewrite_api' with the actual name of the url in your urls.py

    def test_post_request(self):
        # Test a successful post request
        response = self.client.post(
            self.url,
            {
                "postInput": "This is a test post.",
                "emojiNeeded": True,
                "htagNeeded": True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)

        # Test a post request with a short postInput
        response = self.client.post(
            self.url, {"postInput": "Short", "emojiNeeded": True, "htagNeeded": True}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["success"], False)
        self.assertEqual(
            response.data["message"], "The length of the post is too short."
        )

    def test_get_request(self):
        # Test a get request
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], False)
