from django.urls import path

from console.view_operator_page import operator_view
from console.views import home_view
from console.views_cache import cache_view

app_name = 'console'
urlpatterns = [
    path('', home_view, name='home'),
    path('operator/', operator_view, name='operator'),
    path('cache/', cache_view, name='cache'),
]
