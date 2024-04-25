from django.contrib import admin
from django.urls import path
from . import views

# urlpatterns = [path("", views.index), path("rewrite/", views.rewrite, name="rewrite")]
urlpatterns = [
    path("", views.index),
    path("rewrite/", views.RewriteAPI.as_view(), name="rewrite"),
]
