import os
import sys

import django
import codecs

from django.utils import timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "co2.settings")
django.setup()

from account.models import Account
from co2 import settings
from term.models import Term

term_publish = Term.objects.filter(is_publish=True).first()

def create_new_policy_privacy():
    file = codecs.open("term/templates/tos-privacy.html", "r", "utf-8")
    Term.objects.create(
        topic='Term of service privacy policy',
        body=file.read(),
        revision=0,
        content_type=settings.CONTENT_TYPE('term.term'),
        content_id=None,
        is_publish=True,
        datetime_publish=timezone.now()
    )
    Account.objects.all().update(is_accepted_active_consent=False)

if term_publish:
    term_publish.is_publish = False
    term_publish.is_display = False
    term_publish.save(update_fields=['is_publish', 'is_display', 'datetime_update'])

create_new_policy_privacy()
