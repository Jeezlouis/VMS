from django.urls import path
from . import views

app_name = 'VMS'

urlpatterns = [
    path('visitor/', views.visitor, name='visitor'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('assets/', views.assets, name='assets'),
    path('download-asset-qr/<int:asset_id>/', views.download_asset_qr, name='download_asset_qr'),
    path('edit-asset/<int:asset_id>/', views.edit_asset, name='edit_asset'),
    path('delete-asset/<int:asset_id>/', views.delete_asset, name='delete_asset'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reports/', views.reports, name='reports'),
    path('users/', views.users, name='users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('visitor_dashboard/', views.visitor_dashboard, name='visitor_dashboard'),
    path('edit-visitor/<int:visitor_id>/', views.edit_visitor, name='edit_visitor'),
    path('delete-visitor/<int:visitor_id>/', views.delete_visitor, name='delete_visitor'),
    path('visitor_registration/', views.visitor_registration, name='visitor_registration'),
    path('check-pre-registration/', views.check_pre_registration, name='check_pre_registration'),
    path('visitor/', views.visitor, name='visitor'),   
    path('verify-visitor/', views.verify_visitor, name='verify_visitor'),
    path('download-badge/<int:visitor_id>/', views.download_badge, name='download_badge'),
    path('download-asset-badge/<int:asset_id>/', views.download_asset_badge, name='download_asset_badge'),
     path('generate-qr-code/<int:asset_id>/', views.generate_qr_code, name='generate_qr_code'),
    path('', views.welcome_view, name='welcome'), 
    path('logout/', views.user_logout, name='logout'), 
]