"""
URL routes for the Classifier application.
"""

from django.urls import path
from . import views

app_name = 'classifier'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('predict/', views.upload_view, name='upload'),
    path('predictions/', views.history_view, name='history'),
    path('predictions/<int:pk>/', views.prediction_result, name='prediction_result'),
    path('predictions/<int:pk>/detail/', views.prediction_detail, name='prediction_detail'),
    path('predictions/<int:pk>/delete/', views.prediction_delete, name='prediction_delete'),
]
