from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from shop import settings
from store.views import index, about, legal_notice

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('about/', about, name='about'),
    path('legal/', legal_notice, name='legal-notice'),
    path('account/', include('accounts.urls')),
    path('store/', include('store.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
