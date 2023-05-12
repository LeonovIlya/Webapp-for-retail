from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from authorization.views import profileView


urlpatterns = [
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('shop/', include('backend.urls', namespace='backend')),
    path('auth/', include(('authorization.urls', 'authorization'),
         namespace='authorization')),
    path('authorization/profile/', profileView, name='profile'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


