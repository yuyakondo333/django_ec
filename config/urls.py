from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('order/', include('order.urls')),
    path('admin/', include('custom_admin.urls', namespace='custom_admin')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
