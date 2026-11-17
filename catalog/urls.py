from django.urls import path
from . import views

urlpatterns = [
    # Главная и авторизация
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Личный кабинет пользователя
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('request/create/', views.create_request_view, name='create_request'),
    path('request/<int:pk>/delete/', views.delete_request_view, name='delete_request'),

    # ПАНЕЛЬ АДМИНИСТРАТОРА
    path('superadmin/', views.superadmin_panel, name='superadmin_panel'),
    path('superadmin/status/<int:pk>/', views.change_status, name='change_status'),
    path('superadmin/categories/', views.manage_categories, name='manage_categories'),
    path('superadmin/categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
]