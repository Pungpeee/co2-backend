from rest_framework.routers import DefaultRouter
from .views import MailerView
from django.conf.urls import url
from django.urls import include


router = DefaultRouter()

router.register(r'', MailerView)

urlpatterns = [
    url(r'^', include(router.urls)),
]
