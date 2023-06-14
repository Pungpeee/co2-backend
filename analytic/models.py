import datetime

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from utils.ip import get_client_ip


class ContentView(models.Model):
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField(db_index=True)

    count = models.PositiveIntegerField(default=0)
    monthly_count = models.PositiveIntegerField(default=0)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        default_permissions = ()
        ordering = ['-datetime_update']

    def __str__(self):
        return str(self.content_type) + '_' + str(self.content_id)

    @staticmethod
    def push(request, content_type, content_id, source=-1):
        from utils.redis import push, length
        import json
        push('content_view', json.dumps({
            'account_id': request.user.id,
            'content_type_id': content_type.id,
            'content_id': content_id,
            'ip': get_client_ip(request),
            'source': source,
        }))

    @staticmethod
    def pull(content_type, content_id):
        from .caches import cache_content_view
        return cache_content_view(content_type, content_id)

    @staticmethod
    def pull_count(content_type, content_id):
        from .caches import cache_content_view_count
        return cache_content_view_count(content_type, content_id)

    @staticmethod
    def pull_list_by_content_id_list(content_type, content_id_list):
        return ContentView.objects.filter(
            content_type=content_type,
            content_id__in=content_id_list
        )

    # TODO: Remove
    # def update_count(self):
    #     from .caches import cache_content_view_count_set
    #     self.count = ContentViewLog.objects.filter(
    #         content_type_id=self.content_type_id,
    #         content_id=self.content_id
    #     ).count()
    #     self.save(update_fields=['count'])
    #     cache_content_view_count_set(self.content_type_id, self.content_id, self.count)


class ContentViewLog(models.Model):
    SOURCE = (
        (-1, _('(Not set)')),

        (0, _('Web')),
        (1, _('Mobile')),  # Deprecated
        (3, _('Android')),
        (4, _('iOS')),

        (10, _('Dashboard')),
    )

    TYPE = (
        (0, _('User')),
        (1, _('Admin')),
    )

    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField(db_index=True)

    source = models.IntegerField(choices=SOURCE, default=-1, db_index=True)

    ip = models.GenericIPAddressField(null=True)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        default_permissions = ()
        ordering = ['-datetime_create']

    def __str__(self):
        return '%s_%s' % (self.account, self.ip)


class Session(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    session_key = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    source = models.IntegerField(choices=ContentViewLog.SOURCE, default=-1, db_index=True)
    ip = models.GenericIPAddressField(null=True)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        default_permissions = ()
        ordering = ['-datetime_create']

    @staticmethod
    def push(account, session_key, source, ip):
        from django.utils import timezone
        latest_session = Session.objects.filter(account=account, source=source).order_by('datetime_create').last()
        if latest_session:
            diff = timezone.now() - latest_session.datetime_create
            if diff.total_seconds() > 300:
                return Session.objects.create(account=account, source=source, ip=ip)
            else:
                return None
        return Session.objects.create(account=account, session_key=session_key, source=source, ip=ip)

    # @staticmethod
    # def push_redis(request, source):
    #     from utils.redis import push
    #     from django.utils import timezone
    #     import json
    #     push('session_data', json.dumps({
    #         'account_id': request.user.id,
    #         'ip': get_client_ip(request),
    #         'source': source,
    #         'datetime_create': str(timezone.now())
    #     }))

    @staticmethod
    def get_session_count(date):
        return Session.objects.filter(datetime_create__date=date).count()

    @staticmethod
    def get_visitor_count(date):
        return Session.objects.filter(datetime_create__date=date).values('account_id').distinct().count()

    def push_log(self):
        date = self.datetime_create.date()
        SessionLog.push(date)
        VisitorLog.push(date)


class SessionLog(models.Model):
    count = models.PositiveIntegerField(default=0)  # Count session
    date = models.DateField(db_index=True)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        default_permissions = ()
        ordering = ['date']

    @staticmethod
    def push(date, increment_value=-1):
        session_log = SessionLog.objects.filter(date=date).first()
        if session_log and increment_value > -1:
            session_log.count += increment_value
            session_log.save(update_fields=['count', 'datetime_update'])
        elif session_log:
            session_log.update()
        else:
            session_log = SessionLog.objects.create(count=increment_value, date=date)
        return session_log

    def update(self):
        self.count = Session.get_session_count(self.date)
        self.save(update_fields=['count', 'datetime_update'])


class VisitorLog(models.Model):
    count = models.PositiveIntegerField(default=0)  # Count unique visitor
    date = models.DateField(db_index=True)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        default_permissions = ()
        ordering = ['date']

    @staticmethod
    def push(date):
        visitor_log = VisitorLog.objects.filter(date=date).first()
        if visitor_log:
            visitor_log.update()
        else:
            visitor_log = VisitorLog.objects.create(count=Session.get_visitor_count(date), date=date)
        return visitor_log

    def update(self):
        self.count = Session.get_visitor_count(self.date)
        self.save(update_fields=['count'])


class Session2(models.Model):
    date = models.DateField(db_index=True)
    count = models.PositiveIntegerField(default=0)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        default_permissions = ()
        ordering = ['date']

    @staticmethod
    def pull(date):  # TODO: cache
        session = Session2.objects.filter(date=date).first()
        if session is None:
            session = Session2.objects.create(
                date=date
            )
        return session

    @staticmethod
    def push(account, session_key, source, ip):
        SessionLog2.push(account.id, session_key, source, ip)

    def update_count(self):
        session_log_list = SessionLog2.objects.filter(
            date=self.date
        )
        self.count = session_log_list.count()
        self.save(update_fields=['count', 'datetime_update'])

        user = User.pull(self.date)
        user.count = session_log_list.values('account_id').distinct().count()
        user.save(update_fields=['count', 'datetime_update'])


class User(models.Model):
    date = models.DateField(db_index=True)
    count = models.PositiveIntegerField(default=0)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        default_permissions = ()
        ordering = ['date']

    @staticmethod
    def pull(date):  # TODO: cache
        user = User.objects.filter(date=date).first()
        if user is None:
            user = User.objects.create(
                date=date
            )
        return user


class SessionLog2(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    date = models.DateField(db_index=True)
    session_key = models.CharField(max_length=255, db_index=True)
    count = models.PositiveIntegerField(default=1)

    source = models.IntegerField(choices=ContentViewLog.SOURCE, default=-1, db_index=True)
    ip = models.GenericIPAddressField(null=True)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        default_permissions = ()
        ordering = ['-datetime_create']
        index_together = [
            ['date', 'session_key']
        ]

    @staticmethod
    def pull_count(account):
        return SessionLog2.objects.filter(account_id=account.id).count()

    @staticmethod
    def push(account_id, session_key, source, ip):
        pass
        # from utils.redis import push, length
        # import json
        # from django.utils import timezone
        # datetime_create = str(timezone.now())
        # date = str(timezone.now().date())
        # push('session_log', json.dumps({
        #     'account_id': account_id,
        #     'date': date,
        #     'datetime_create': datetime_create,
        #     'session_key': session_key,
        #     'ip': ip,
        #     'source': source,
        #     'count': 1
        # }))


class DurationLog(models.Model):
    date = models.DateField(db_index=True)
    duration = models.DurationField(default=datetime.timedelta(0))

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        default_permissions = ()
        ordering = ['date']

    @staticmethod
    def get_count_duration(duration):
        duration = duration.aggregate(duration_sum=Sum('duration'))
        return duration['duration_sum'].total_seconds() if duration['duration_sum'] else 0

    @staticmethod
    def push(date, duration_sum):
        progress_video_list = DurationLog.objects.filter(date=date).first()
        if progress_video_list:
            progress_video_list.duration_sum = duration_sum
            progress_video_list.save()
        else:
            DurationLog.objects.create(date=date, duration=duration_sum)
        return DurationLog
