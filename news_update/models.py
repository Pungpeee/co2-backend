from django.conf import settings
from django.db import models
from django.db.models import Count

from utils.model_permission import DEFAULT_PERMISSIONS


class NewsUpdate(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)  # Create user
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    short_desc = models.TextField(blank=True)

    sort = models.IntegerField(default=0, db_index=True)

    is_display = models.BooleanField(default=False)
    is_pin = models.BooleanField(default=False, db_index=True)
    is_notification = models.BooleanField(default=False)
    count_notification = models.IntegerField(default=0)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='update_by')

    class Meta:
        verbose_name = 'news_update.newsupdate'
        ordering = ['-datetime_update']  # 2018-04-25: Change from sort to datetime update
        default_permissions = DEFAULT_PERMISSIONS

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        from news_update.caches import clear_caches
        clear_caches(self)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        from news_update.caches import clear_caches
        clear_caches(self)
        super().delete(*args, **kwargs)

    def get_log(self):
        return {
            'name': self.name,
            'desc': self.desc,
            'is_notification': self.is_notification,
            'is_display': self.is_display,
            'is_pin': self.is_pin
        }

    def clean_desc(self):
        import re
        from bs4 import BeautifulSoup

        html = self.desc
        if not html and len(html) == 0:
            return ''

        soup = BeautifulSoup(html, 'lxml')

        # Remove Tag
        remove_tag_list = ['table']
        for remove_tag in soup(remove_tag_list):
            remove_tag.extract()

        # Custom Bullet Tag
        for bullet_tag in soup.find_all(['ul', 'ol']):
            if bullet_tag.name == 'ul':
                for bullet in bullet_tag.select('li'):
                    bullet.string = u'• ' + bullet.string

            if bullet_tag.name == 'ol':
                for i, bullet in enumerate(bullet_tag.select('li')):
                    bullet.string = '%s. %s' % (i + 1, bullet.string)

        text = soup.get_text()

        # Remove iframe tag
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'(?:<iframe[^>]*)(?:(?:/>)|(?:>.*?</iframe>))', '', text)
        lines = [line.rstrip() for line in text.splitlines()]
        chunks = (phrase.rstrip() for line in lines for phrase in line.split('  '))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        self.short_desc = text
        self.save()
        return text

    @staticmethod
    def pull(id):  # TODO: cached
        return NewsUpdate.objects.filter(id=id).first()

    @staticmethod
    def pull_announcement():
        from .caches import cached_news_announcement
        return cached_news_announcement()

    @staticmethod
    def pull_list():
        from .caches import cache_news_update_pull_list
        return cache_news_update_pull_list()

    @staticmethod
    def pull_home_list():
        from .caches import cache_news_update_home_pull_list
        return cache_news_update_home_pull_list()

    @staticmethod
    def count_unread(account):  # un-used
        from analytic.models import ContentViewLog

        if not account.is_authenticated:
            account = None

        id_list = ContentViewLog.objects.filter(
            account=account,
            content_type=settings.CONTENT_TYPE('news_update.newsupdate')
        ).values_list('content_id', flat=True)
        count_unread = NewsUpdate.objects.exclude(id__in=id_list).aggregate(count_unread=Count('id'))
        return count_unread

    @staticmethod
    def check_sort():
        sort = 0
        for _ in NewsUpdate.objects.all():
            sort += 1
            if _.sort != sort:
                _.sort = sort
                _.save(update_fields=['sort'])

    def is_read(self, account):  # un-used
        from analytic.models import ContentViewLog
        content_type = settings.CONTENT_TYPE('news_update.newsupdate')
        if account.is_authenticated:
            return ContentViewLog.objects.filter(
                content_type=content_type, content_id=self.id, account=account
            ).exists()
        return False

    def pull_log(self, account_id):
        from news_update.caches import cache_news_update_log
        news_update_log = cache_news_update_log(self.id, account_id)
        return news_update_log

    def push_log(self, account_id):
        from news_update.caches import cache_news_update_log_delete
        NewsUpdateLog.objects.update_or_create(
            news_update_id=self.id,
            account_id=account_id,
            defaults={'is_read': True}
        )
        cache_news_update_log_delete(self.id, account_id)
        return self.pull_log(account_id)


class Gallery(models.Model):
    news_update = models.ForeignKey(NewsUpdate, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news_update/%Y/%m/', blank=True)
    is_cover = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-is_cover', 'id']
        default_permissions = ()


class NewsUpdateLog(models.Model):
    news_update = models.ForeignKey(NewsUpdate, on_delete=models.CASCADE)
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, db_index=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        default_permissions = ()
