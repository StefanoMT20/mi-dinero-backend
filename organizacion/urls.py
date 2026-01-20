"""
URL configuration for organizacion project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.users.views import UserSettingsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/', include('apps.finances.urls')),
    path('api/', include('apps.goals.urls')),
    path('api/', include('apps.budgets.urls')),
    path('api/', include('apps.installments.urls')),
    path('api/settings/', UserSettingsView.as_view(), name='user_settings'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
