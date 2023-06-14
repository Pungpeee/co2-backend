from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from config.models import Config


class FacebookLoginTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_register(self):

        payload = {
            "social_type": "facebook",
            "token": "EAAD42tiUwQ8BAMqqwd4I9LMZBqbwTw83oy4LKLb765Q4DxioXr"
                     "xslIOtRhUhkrON3yMveBj718ZCYi16kReRquf3V7K4PPOklAchHojUPpEZC1j"
                     "QZArIZCYarBzXjOnZCjkcqqXMmILeLVHRJII32TtaS17DdzQCOFxYNntgTrMJqZAqhoxcjK"
                     "OqeRvpoRRGzTZBJH0dzVnnt"
        }
        response = self.client.post('/api/account/login/social/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
