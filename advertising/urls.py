"""advertising URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from advertising import settings
from screens import views as screenviews
from room_schedules import urls as room_schedules_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/admin/')),
    path('screen/', screenviews.view_screen_automatic),
    path('screen/<int:screen_id>', screenviews.view_screen, name="screens/screen_view"),
    path('playlist/<int:playlist_id>', screenviews.view_playlist, name="screens/playlist_view"),
    path('api/screen/', screenviews.view_screen_automatic_json),
    path('api/screen/<int:screen_id>', screenviews.view_screen_json, name="screens/screen_view_json"),
    path('api/playlist/<int:playlist_id>', screenviews.view_playlist_json, name="screens/playlist_view_json"),
    path('api/playlist_tree', screenviews.view_playlist_tree_json, name="screens/playlist_tree_json"),
    path('meta', screenviews.get_meta, name="screen-meta-view"),
    path('api/meta', screenviews.get_meta, name="screen-meta-view"),
    path('api/meta/<int:screen_id>', screenviews.get_meta_screen, name="screen-meta-view-specific"),
    path('event_schedules/', include(room_schedules_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
