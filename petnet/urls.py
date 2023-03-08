from django.conf import settings
from django.conf.urls.static import static
from xml.etree.ElementInclude import include
from django.contrib import admin
from django.urls import path, include
from core.views import frontpage, about, frontpage2

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('about/', about, name='about'),
    path('f2/', frontpage2, name='frontpage2'),
    path('adminStore/',include('adminStore.urls')),
    path('', include('userprofile.urls')),    
    path('', include('Shipping.urls')),    
    path('', include('store.urls')),
    path('', frontpage, name='frontpage'),
    
    
    
]
if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)   
       