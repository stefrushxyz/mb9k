"""mb9k URL Configuration"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'mb9k'
admin.site.site_title = ('mb9k')

urlpatterns = [
    path('', include('app.urls', namespace='app'), name='app'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, \
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static('/favicon.ico', document_root='app/static/favicons/favicon.ico')

