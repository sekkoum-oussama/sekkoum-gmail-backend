from django.contrib import admin
from django.urls import path, include
from gmail_project.aset_links_view import serve_assetlinks
from users.views import GoogleLogin
from django.conf.urls.static import static 
from django.conf import settings


urlpatterns = [
    path(".well-known/assetlinks.json", serve_assetlinks, name="assetlinks"),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('auth/', include('dj_rest_auth.urls')),
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('messages/', include('message.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)