from rest_framework.routers import DefaultRouter
from .views import EventView
from django.conf.urls import url
from django.urls import include


router = DefaultRouter()

router.register(r'', EventView)

urlpatterns = [
    url(r'^', include(router.urls)),
]
