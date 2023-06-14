import os
import sys

# import django


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "co2.settings")
# django.setup()

from utils.check_service import check_service

if __name__ == '__main__':
    for key, values in check_service().items():
        print('%s : %s' % (key, values))
