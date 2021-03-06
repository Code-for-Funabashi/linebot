from django.urls import path, re_path

from . import views
from django.views.generic.base import TemplateView # new

urlpatterns = [
    path('callback/', views.callback),
]