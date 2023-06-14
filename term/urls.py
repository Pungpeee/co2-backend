from rest_framework import routers

#from course.dashboard.views_term import TermView,
from .views import TermView, TermViewAllowAll
router = routers.DefaultRouter()

# router.register(r'', TermView)
router.register('', TermView)
router.register('', TermViewAllowAll)

urlpatterns = router.urls
