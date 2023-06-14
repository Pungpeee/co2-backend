from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from .views_monitor import MonitorCeleryView
from rest_framework_swagger.views import get_swagger_view
# from account.login_vekin_sso import Client

# sso_client = Client(settings.SSO_SERVER, settings.SSO_PUBLIC_KEY, settings.SSO_PRIVATE_KEY)
subpath = 'backend/'

urlpatterns_api_user = [
    path(subpath + 'api/account/', include('account.urls')),
    path(subpath + 'api/activity/', include('activity.urls')),
    path(subpath + 'api/config/', include('config.urls')),
    path(subpath + 'api/inbox/', include('inbox.urls')),
    path(subpath + 'api/log/', include('log.urls')),
    path(subpath + 'api/notification/', include('notification.urls')),
    path(subpath + 'api/scb_pg/', include('scb_pg.urls')),
    path(subpath + 'api/term/', include('term.urls')),
    path(subpath + 'api/transaction/', include('transaction.urls')),
    path(subpath + 'api/card/', include('card.urls')),
    path(subpath + 'api/event/', include('event.urls')),
    path(subpath + 'api/mailer/', include('mailer.urls')),

    path(subpath + 'api/monitor/celery/', MonitorCeleryView.as_view()),
    # path(subpath + 'api/sso_client/', include(sso_client.get_urls()))
]

urlpatterns_swagger = [
    path(subpath + 'api/', get_swagger_view(title='API Docs.', patterns=urlpatterns_api_user)),
]

urlpatterns = [
    path('console/', include('console.urls')),
]

urlpatterns += urlpatterns_api_user

if settings.SWAGGER_SETTINGS['IS_ENABLE']:
    urlpatterns += urlpatterns_swagger

if settings.IS_HIDE_ADMIN_URL:
    urlpatterns += [
        path(subpath + 'hidden-admin/', admin.site.urls),  # Honda Pen-Test
    ]
else:
    urlpatterns += [
        path(subpath + 'xadmin12324/', admin.site.urls),
    ]

urlpatterns += [
    re_path(r'^backend/media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^backend/static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^backend/default/(?P<path>.*)$', serve, {'document_root': settings.DEFAULT_ROOT}),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls))
    ]
