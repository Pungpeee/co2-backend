from rest_framework import routers

from .views import TransactionView
from .views_swap import TransactionSwapView
from .views_topup import TransactionTopUpView

router = routers.DefaultRouter()
router.register(r'swap', TransactionSwapView)
router.register(r'top-up', TransactionTopUpView)
router.register(r'', TransactionView)

app_name = 'transaction'
urlpatterns = router.urls
