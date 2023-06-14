from django.contrib.contenttypes.models import ContentType
from django.db import models


class ConfigNotification(models.Model):

    name = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType, related_name='config_notification_set', on_delete=models.CASCADE)
    is_use = models.BooleanField(default=False)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.content_type.name


