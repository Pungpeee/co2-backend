from rest_framework.routers import DefaultRouter
from .views import CardView
from django.conf.urls import url
from django.urls import include


router = DefaultRouter()

router.register(r'', CardView)

urlpatterns = [
    url(r'^', include(router.urls)),
]
