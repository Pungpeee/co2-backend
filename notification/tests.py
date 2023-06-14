from django.conf import settings
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from account.tests import create_super_user

from inbox.models import Inbox


def mock_data_read_ontification_content(inbox):
    data = {}
    data['is_read'] = True
    id_list = []
    contents = inbox.content_set.all().order_by('?')
    for content in contents:
        id_list.append(content.id)
    data['inbox_id'] = inbox.id
    data['content_list'] = id_list
    return data



def mock_data_notification(account):
    title = 'Tittle is Test'
    body = 'Body is Test'
    for index in range(5):
        Inbox.objects.create(account=account, title=title, body=body, type=2, status=1)


def mock_data_notification_is_read(channel):
    inbox = Inbox.objects.all().order_by('?').last()
    data = {}
    data['id_list'] = [inbox.id]
    data['is_read'] = True
    data['channel'] = channel
    return data


class TestCaseFCM(TestCase):
    def setUp(self):
        self.account = create_super_user()
        self.client = APIClient()
        self.client.force_authenticate(self.account)
        self.data = {
            "name": "Django Register FCM Test Case",
            "registration_id": "I3NJ2sIN2-2Jds:2ejUJds2Knd",
            "active": True,
            "type": 'ios'
        }
    
    def test_register(self):
        response = self.client.post('/api/notification/fcm/register/', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class TestNotification(TestCaseFCM):

    def test_count(self):
        response = self.client.get('/api/notification/count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_count_is_read_true(self):
        data = {}
        response = self.client.post('/api/notification/open/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list(self):
        response = self.client.get('/api/notification/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

