from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]

# Always serve media files (for production and development)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)