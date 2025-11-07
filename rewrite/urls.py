from django.contrib import admin
from django.urls import path
from . import views

app_name = 'rewrite'

urlpatterns = [
    path("", views.index, name="index"),
    path("rewrite/", views.RewriteAPI.as_view(), name="rewrite"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("pricing/", views.pricing, name="pricing"),
    path("upgrade/", views.upgrade_plan, name="upgrade_plan"),
]

handler404 = "rewrite.views.error_404"
