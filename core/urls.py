# pylint: disable=invalid-name
from django.urls import path, include

dashboard_urls = [
]

urlpatterns = [
    path('', include(dashboard_urls)),
]
