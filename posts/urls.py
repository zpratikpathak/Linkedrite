from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('posts/', views.post_list, name='list'),
    path('posts/create/', views.post_create, name='create'),
    path('posts/<int:post_id>/', views.post_detail, name='detail'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='edit'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='delete'),
    path('posts/calendar/', views.calendar_view, name='calendar'),
    path('api/ai/generate-text/', views.ai_generate_text, name='ai_generate_text'),
    path('api/ai/generate-image/', views.ai_generate_image, name='ai_generate_image'),
]
