"""
URL configuration for AyuMorph project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import accounts.views as account_views
import classifier.views as classifier_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('classifier.urls')),
    path('accounts/', include('accounts.urls')),
    path('plants/', include('plants.urls')),

    # Top-level direct shortcuts
    path('home/', classifier_views.home, name='home'),
    path('about/', classifier_views.about, name='about'),
    path('dashboard/', classifier_views.dashboard, name='dashboard'),
    path('predict/', classifier_views.upload_view, name='predict'),
    path('profile/', account_views.profile_view, name='profile'),
    path('login/', account_views.login_view, name='login'),
    path('register/', account_views.register_view, name='register'),
    path('logout/', account_views.logout_view, name='logout'),
]

# Serve media and static assets during local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom HTTP Error Handlers
handler400 = 'classifier.views.error_400'
handler403 = 'classifier.views.error_403'
handler404 = 'classifier.views.error_404'
handler500 = 'classifier.views.error_500'
