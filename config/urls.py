from rest_framework import routers

from .views import FeatureView

router = routers.DefaultRouter()
router.register(r'', FeatureView)

app_name = 'config'
urlpatterns = router.urls
