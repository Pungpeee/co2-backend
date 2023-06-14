from rest_framework import routers

from .views import NewsUpdateView
from .views_pin import NewsUpdatePinView
from .news_update_v2.views import NewsUpdateView as NewsUpdateViewV2

router = routers.DefaultRouter()
router.register(r'pin', NewsUpdatePinView)
router.register(r'v2', NewsUpdateViewV2)
router.register(r'', NewsUpdateView)

urlpatterns = router.urls
