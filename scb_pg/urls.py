from rest_framework import routers

from .views_confirmation import SCBPaymentConfirmationSerializerView

router = routers.DefaultRouter()
router.register(r'payment/confirm', SCBPaymentConfirmationSerializerView)

app_name = 'scb_pg'
urlpatterns = router.urls
