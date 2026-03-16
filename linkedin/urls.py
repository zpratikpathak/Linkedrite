from django.urls import path
from . import views

app_name = 'linkedin'

urlpatterns = [
    path('connect/', views.connect, name='connect'),
    path('callback/', views.callback, name='callback'),
    path('accounts/', views.accounts_list, name='accounts'),
    path('accounts/json/', views.accounts_json, name='accounts_json'),
    path('disconnect/<int:account_id>/', views.disconnect, name='disconnect'),
]
