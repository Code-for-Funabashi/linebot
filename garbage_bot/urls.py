from django.urls import path, re_path

from . import views, tests
from django.views.generic.base import TemplateView  # new

urlpatterns = [
    path("callback/", views.callback),
    path("test/", tests.test_server),
]
