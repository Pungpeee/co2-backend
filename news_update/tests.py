from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from account.tests import create_super_user, create_user
from utils.tests import generate_image, IMAGE_BASE64_EXAMPLE
from .models import NewsUpdate


def _create_announcement(account, name, desc, is_pin, is_display, is_notification):
    announcement = NewsUpdate.objects.all().order_by('sort')

    if announcement.first():
        get_object = announcement.first()
        sort = get_object.sort
    else:
        sort = 0

    return NewsUpdate.objects.create(account=account,
                                     name=name,
                                     desc=desc,
                                     is_pin=is_pin,
                                     is_display=is_display,
                                     is_notification=is_notification,
                                     sort=sort)


class APIDashboardTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        account = create_super_user()
        self.base_url = '/api/dashboard/news-update/'
        self.client.force_authenticate(account)

    def test_get_list(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_success(self):
        data = mock_data_create()
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_post_cannot_success(self):
    #     mock_data_is_pin(is_pin=True, is_display=True)
    #     data = mock_data_create()
    #     response = self.client.post(self.base_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_is_display_false_and_is_pin_false_success(self):
        mock_data_is_pin(is_pin=True, is_display=True, is_notification=True)

        data = mock_data_create()
        data['is_display'] = False
        data['is_pin'] = False
        data['is_notification'] = False
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # set is_display = True
    # def test_post_is_display_false(self):
    #     data = mock_data_create()
    #     data['is_display'] = False
    #     response = self.client.post(self.base_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_is_pin_true_and_is_disply_true_patch(self):
        mock_data_is_pin(is_display=False, is_pin=False, is_notification=True)
        announcement = get_object_random()
        url = '%s%s/' % (self.base_url, announcement.id)
        # show(announcement.id)
        data = mock_data_patch_is_pin_and_is_display(is_pin=True, is_display=True, is_notification=True)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # show(announcement.id)

    def test_is_pin_false_and_is_disply_true_patch(self):
        mock_data_is_pin(is_display=True, is_pin=False, is_notification=True)
        announcement = get_object_random()
        url = '%s%s/' % (self.base_url, announcement.id)
        # show(announcement.id)
        data = mock_data_patch_is_pin_and_is_display(is_pin=True, is_display=True, is_notification=True)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # show(announcement.id)


class TestAPIImage(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(create_super_user())
        mock_data_is_pin(is_display=False, is_pin=False, is_notification=True)
        self.announcement = get_object_random()
        self.base_url = '/api/dashboard/news-update/%s/gallery/' % self.announcement.id

    def test_create(self):
        data = mock_data_image(is_cover=False)
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_unlimit(self):
        mock_image(self.announcement, 10)
        data = mock_data_image(is_cover=True)
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_path_is_false(self):
        mock_image(self.announcement, 9, is_cover=True)
        data = mock_data_image(is_cover=False)
        image = get_image_random(self.announcement)
        url = '%s%s/' % (self.base_url, image.id)
        data.pop('image')
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_path_is_true(self):
        mock_image(self.announcement, 9, is_cover=True)
        data = mock_data_image(is_cover=True)
        image = get_image_random(self.announcement)
        url = '%s%s/' % (self.base_url, image.id)
        data.pop('image')
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for image_object in self.announcement.gallery_set.exclude(id=image.id):
            self.assertEqual(image_object.is_cover, False)


class AnnounementAPITesstCase(TestCase):
    def setUp(self):
        mock_announcement_is_true()
        self.client = APIClient()
        self.client.force_authenticate(create_super_user())
        self.base_url = '/api/news-update/'

    def test_get_all(self):
        response = self.client.get(self.base_url)
        result = response.data.get('results')
        content = result[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(content.get('is_read'))

    # TODO: Not realtime views
    def test_get_object(self):
        content = get_object_random()
        url = '%s%s/' % (self.base_url, content.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertTrue(response.data.get('is_read'))


def mock_data_image(is_cover):
    data = {
        'image': IMAGE_BASE64_EXAMPLE,
        'is_cover': is_cover
    }
    return data


def mock_data_create():
    data = {
        'name': "Python Programing",
        'desc': "<p>Desc</p>",
        'is_pin': True,
        'is_display': True,
        'is_notification': True,
    }
    return data


def mock_data_patch_is_pin_and_is_display(is_display, is_pin, is_notification):
    data = {
        "is_display": is_display,
        "is_pin": is_pin,
        "is_notification": is_notification
    }
    return data


def get_object_random():
    return NewsUpdate.objects.all().order_by('?').first()


def get_announcement(id):
    return NewsUpdate.objects.get(id=id)


def mock_data_sort(position):
    data = {}
    get_object = NewsUpdate.objects.all().order_by('?').first()
    data['id'] = get_object.id
    data['position'] = position
    return data


def mock_data_is_pin(is_pin, is_display, is_notification):
    for index in range(5):
        NewsUpdate.objects.create(account=create_super_user(), is_display=is_display, is_pin=is_pin,
                                  is_notification=is_notification, sort=index)


def mock_announcement_is_true():
    for index in range(10):
        account = create_user()
        if (index % 2) is not 0:
            is_pin = False
        else:
            is_pin = True

        is_display = True
        is_notification = True

        name = 'Programming'
        desc = 'Welcome to programming world and python language.'
        _create_announcement(account, name, desc, is_pin, is_display, is_notification)


def mock_announcement():
    for index in range(10):
        account = create_user()
        if (index % 2) is not 0:
            is_pin = False
        else:
            is_pin = True
        if index < 6:
            is_display = True
            is_notification = True
        else:
            is_display = False
            is_notification = False
        name = 'Programming'
        desc = 'Welcome to programming world and python language.'
        _create_announcement(account, name, desc, is_pin, is_display, is_notification)


def get_image_random(announcement):
    return announcement.gallery_set.all().order_by('?').first()


def mock_image(announcement, size, is_cover=False):
    for index in range(size):
        announcement.gallery_set.create(image=generate_image(), is_cover=is_cover)
