import random
import string

from django.test import TestCase

# Create your tests here.
from account.models import Account


def create_super_user(username=None, email=None, password=None):
    if username is None:
        username = ''.join(random.sample(string.ascii_lowercase, 6))
    if email is None:
        email = '%s@domain.com' % username
    if password is None:
        password = '1234'
    account = Account.objects.create_superuser(username, password)
    account.email = email
    account.save(update_fields=['email'])
    return account