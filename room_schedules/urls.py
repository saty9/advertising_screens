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
from django.urls import path

from .views import show_venue, show_room, show_room_display, room_led_status

urlpatterns = [
    path('<int:venue_id>', show_venue, name="event_schedule/venue"),
    path('<int:venue_id>/<int:room_id>', show_room, name="event_schedule/room"),
    path('<int:venue_id>/<int:room_id>/tablet', show_room_display, name="event_schedule/room_display"),
    path('<int:venue_id>/<int:room_id>/tablet/LED', room_led_status, name="event_schedule/room_led"),
]
