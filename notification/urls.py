from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework import routers

from .views import InboxView
from .views_count import CountUnreadViewSet, ReadCountViewSet
from .views_status import NotificationStatusView
from .views_fcm import FCMView

router = routers.DefaultRouter()

router.register('', InboxView)
router.register('status', NotificationStatusView)
router.register('count', CountUnreadViewSet)
router.register('open', ReadCountViewSet)

router.register('device', FCMDeviceAuthorizedViewSet)
router.register('fcm/register', FCMView)

urlpatterns = router.urls
