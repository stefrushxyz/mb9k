from django.urls import include, path

from . import views
from .api import urls as api_urls

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(api_urls), name='api'),
]

