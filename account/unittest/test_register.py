from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from config.models import Config

class RegisterTestCase(TestCase):

    def setUp(self):
        config = Config.pull('config-is-enable-register')
        config.value = True
        config.save(update_fields=['value', 'datetime_update'])
        self.client = APIClient()

    def test_register(self):

        payload = {
            "username": "beer",
            "password": "1aA@!234",
            "is_remember": False,
            "language": "",
            "confirm_password": "1aA@!234",
            "email": "dd@gmail.com",
            "title_name": "mr",
            "first_name": "qwer",
            "last_name": "qwer",
            "is_subscribe": False,
            "address": "test_address",
            "experience": "22222",
            "whatever": "testtt",
            "is_accepted_active_consent": True
        }

        response = self.client.post('/api/account/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_428_PRECONDITION_REQUIRED)

    # def test_register_with_not_accept_consent_on_no_publish_term(self):
    #
    #     payload = {
    #         "username": "beer1",
    #         "password": "1aA@!234",
    #         "is_remember": False,
    #         "language": "",
    #         "confirm_password": "1aA@!234",
    #         "email": "dd1@gmail.com",
    #         "title_name": "mr",
    #         "first_name": "qwer",
    #         "last_name": "qwer",
    #         "is_subscribe": False,
    #         "is_term_and_condition": False,
    #         "address": "test_address",
    #         "experience": "22222",
    #         "whatever": "testtt",
    #         "is_accepted_active_consent": False
    #     }
    #
    #     response = self.client.post('/api/account/register/', payload, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
