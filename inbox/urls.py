from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from .views import InboxView
from .views_count import CountUnreadViewSet, ReadCountViewSet
from .views_status import NotificationStatusView

router = DefaultRouter()
router.register(r'', InboxView)
# router.register('status', NotificationStatusView)
# router.register('count', CountUnreadViewSet)
# router.register('open', ReadCountViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
