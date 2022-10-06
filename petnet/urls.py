from django.conf import settings
from django.conf.urls.static import static
from xml.etree.ElementInclude import include
from django.contrib import admin
from django.urls import path, include
from core.views import frontpage, about

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', about, name='about'),
    path('', include('userprofile.urls')),    
    path('', include('store.urls')),
    path('', frontpage, name='frontpage'),
    
]
if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)   
       