import datetime

from django.shortcuts import render, get_object_or_404


# Create your views here.
from room_schedules.settings import HOUR_BREAK_POINT
from room_schedules.models import Venue, Event, Room


def show_venue(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    events = Event.objects.filter(room__venue=venue, end_time__gte=datetime.datetime.now(), cancelled=False)
    current_date = (datetime.datetime.now() - datetime.timedelta(hours=HOUR_BREAK_POINT)).date()
    return render(request, "room_schedules/dashboard.html", {'events': events, 'current_date': current_date})


def show_room(request, venue_id, room_id):
    room = get_object_or_404(Room, pk=room_id)
    events = Event.objects.filter(room=room, end_time__gte=datetime.datetime.now(), cancelled=False)
    current_date = (datetime.datetime.now() - datetime.timedelta(hours=HOUR_BREAK_POINT)).date()
    return render(request, "room_schedules/dashboard.html", {'events': events, 'current_date': current_date, 'room': room})
