from django.contrib import admin

from .models import ContentView, ContentViewLog, Session, SessionLog, VisitorLog, Session2, SessionLog2, User, \
    DurationLog


@admin.register(ContentView)
class ContentViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type_id', 'content_id', 'count', 'datetime_create', 'datetime_update')
    search_fields = [
        'content_id',
    ]
    list_filter = ('content_type',)


@admin.register(ContentViewLog)
class ContentViewLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type_id', 'content_id', 'datetime_create')
    readonly_fields = ['account', 'content_type']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_id', 'source', 'ip', 'datetime_create')
    actions = ['push_log', ]

    @staticmethod
    def push_log(self, request, queryset):
        map = []
        for session in queryset:
            date = session.datetime_create.date()
            if date not in map:
                map.append(date)
                session.push_log()


@admin.register(SessionLog)
class SessionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'count', 'date', 'datetime_create')
    actions = ['update', ]

    @staticmethod
    def update(self, request, queryset):
        for log in queryset:
            log.update()


@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'count', 'date', 'datetime_create')
    actions = ['update', ]

    @staticmethod
    def update(self, request, queryset):
        for log in queryset:
            log.update()


@admin.register(Session2)
class Session2Admin(admin.ModelAdmin):
    list_display = ('date', 'count', 'datetime_update', 'datetime_create')
    ordering = ['datetime_create']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('date', 'count', 'datetime_update', 'datetime_create')
    ordering = ['datetime_create']


@admin.register(SessionLog2)
class SessionLog2Admin(admin.ModelAdmin):
    list_display = ('account', 'date', 'count', 'source', 'ip', 'datetime_create')
    readonly_fields = ('account',)


@admin.register(DurationLog)
class DurationLogAdmin(admin.ModelAdmin):
    list_display = ('date', 'duration', 'datetime_update', 'datetime_create')
    ordering = ['datetime_create']
