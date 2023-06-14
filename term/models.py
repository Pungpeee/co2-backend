from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models


class Term(models.Model):
    topic = models.CharField(max_length=255, db_index=True, default='')
    body = models.TextField(blank=True)
    revision = models.PositiveIntegerField(default=0, db_index=True)
    is_publish = models.BooleanField(default=False)
    body = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField(null=True, default=0)
    content = GenericForeignKey('content_type', 'content_id')
    is_display = models.BooleanField(default=False, db_index=True)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_publish = models.DateTimeField(db_index=True, null=True, blank=True)

    class Meta:
        ordering = ['-id']

    @property
    def total_accept(self):
        return self.consent_set.all().count()

    @staticmethod
    def pull(content_type, content_id):
        content = Term.objects.filter(content_type=content_type, content_id=content_id).first()
        if content is None:
            content = Term.objects.create(content_type=content_type, content_id=content_id)
        return content

    @staticmethod
    def is_require_accept(content_type, content_id, account):
        return False


class Consent(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True)


class Log(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    payload = models.TextField(blank=True, default='{}')

    class Meta:
        default_permissions = ()